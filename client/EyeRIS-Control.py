import os
import sys
import lcm
import copy
import datetime
import logging
import qdarkstyle
import pyqtgraph as pg
from collections import deque
from data_types import EyeRISDataType
from eyeris import control_status_t, set_light_output_t, set_relays_t, set_zoom_t
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets




## Define main window class from template
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'EyeRIS-Control.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

class LCMManager(QtCore.QThread):

    # signals
    control_status = QtCore.Signal(object)

    def __init__(self, args):
        QtCore.QThread.__init__(self)
        #self.args = args
        logger.info("Initializing handler...")
        self.lc = lcm.LCM('udpm://239.255.76.67:7667?ttl=2')

    def __del__(self):
        self.wait()

    def control_status_handler(self, channel, data):
        status = control_status_t.decode(data)
        self.control_status.emit(status)

    def run(self):

        logger.info("Creating LCM subscriptions")
        self.lc.subscribe('EYERIS_CONTROL_STATUS', self.control_status_handler)

        while self.isRunning:
            self.lc.handle()


class DataLogger:

    def __init__(self, log_path='logs', log_rate=1.0, log_fmt='csv', log_data_type='eyeris_control', lines_per_file=1800):
        self.log_rate = log_rate
        self.log_fmt = log_fmt
        self.log_path = log_path
        self.lines_per_file = lines_per_file
        self.log_data_type = log_data_type
        self.lines_in_file = 0
        self.filename = None

        if log_data_type == 'eyeris_control':
            self.data_type = EyeRISDataType()
        else:
            logger.error('Invalid Data Type for Log File.')
            self.data_type = None

    def write_log(self, data):

        if self.data_type is None:
            logger.info("Do data type defined for log file")
            return

        # Create new file as needed based on line count
        if self.filename is None or self.lines_in_file >= self.lines_per_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
            self.filename = os.path.join(self.log_path, 'EyeRIS-Control-' + timestamp + '.csv')
            self.lines_in_file = 0

        # Open file and write the log info using the defined data type
        with open(self.filename,"a+") as f:
            if self.lines_in_file == 0:
                # write header for CSV
                self.data_type.write_header(f)

            self.data_type.write_data(f, data)
            self.lines_in_file += 1





class MainWindow(TemplateBaseClass):

    def __init__(self, argv):

        QtWidgets.QMainWindow.__init__(self)
        TemplateBaseClass.__init__(self)
        self.setWindowTitle('EyeRIS-Control- Python - Qt')

        # defaults
        self.plot_history = 500

        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)

        # LCM handler
        self.lcm_manager = LCMManager(argv)
        self.lcm_manager.start()

        # Data Logger
        self.data_logger = DataLogger()

        # Light output tracker for resetting light output when it drops
        self.last_light_output = None

        # signals and slots
        self.lightOutputs = []
        self.lightOutputs.append(self.ui.lightOutputSpinBox1)
        self.lightOutputs.append(self.ui.lightOutputSpinBox2)
        self.lightOutputs.append(self.ui.lightOutputSpinBox3)
        self.lightOutputs.append(self.ui.lightOutputSpinBox4)
        self.lightOutputs.append(self.ui.lightOutputSpinBox5)
        self.lightOutputs.append(self.ui.lightOutputSpinBox6)
        for l in self.lightOutputs:
            l.valueChanged.connect(self.update_light_output)

        self.ui.setLightOutput.clicked.connect(self.update_light_output)
        self.ui.setLightOutputToZero.clicked.connect(self.update_light_output_0)
        self.ui.setLightOutputTo85.clicked.connect(self.update_light_output_85)

        self.lcm_manager.control_status.connect(self.update_status)
        self.ui.zoomComboBox.currentTextChanged.connect(self.update_zoom)
        self.ui.cameraButton.clicked.connect(self.update_camera)
        self.ui.lightsButton.clicked.connect(self.update_lights)

        # data structures
        self.temperatures = [deque(), deque()]
        self.humidities = [deque(), deque()]
        self.pressures = [deque(), deque()]
        self.relay_list = [False, False, False, False]

        self.tempIndicators = [self.ui.temp1Indicator, self.ui.temp2Indicator]
        self.humIndicators = [self.ui.humidity1Indicator, self.ui.humidity2Indicator]
        self.pressIndicators = [self.ui.pressure1Indicator, self.ui.pressure2Indicator]

        # GUI style
        self.set_gui_style()

        # Show the main window
        self.show()

    def update_zoom(self, zoom):

        zoom_output = set_zoom_t()
        zoom_output.focal_length = int(zoom.split('m')[0].rstrip(' '))
        self.lcm_manager.lc.publish('EYERIS_ZOOM', zoom_output.encode())


    def update_camera(self):

        if len(self.relay_list) > 0:
            if self.relay_list[3]:
                self.relay_list[3] = False
            else:
                self.relay_list[3] = True

        relay_output = set_relays_t()
        relay_output.nrelays = 4
        relay_output.relays = self.relay_list
        self.lcm_manager.lc.publish('EYERIS_RELAYS', relay_output.encode())

    def update_lights(self):

        if len(self.relay_list) > 0:
            if self.relay_list[0] and self.relay_list[1]:
                self.relay_list[0] = False
                self.relay_list[1] = False
            else:
                self.relay_list[0] = True
                self.relay_list[1] = True

        relay_output = set_relays_t()
        relay_output.nrelays = 4
        relay_output.relays = self.relay_list
        self.lcm_manager.lc.publish('EYERIS_RELAYS', relay_output.encode())

    def update_light_output_0(self, lout):
        light_output = set_light_output_t()
        light_output.nlights = 6
        light_output.lout = []
        for ind in range(0,light_output.nlights):
            logger.info("Setting light " + str(ind) + " to 0 %")
            light_output.lout.append(0)
            self.lightOutputs[ind].blockSignals(True)
            self.lightOutputs[ind].setValue(0)
            self.lightOutputs[ind].blockSignals(False)
        #light_output.lout = [lout for dim0 in range(0, light_output.nlights)]
        self.lcm_manager.lc.publish('EYERIS_LIGHT_OUTPUT', light_output.encode())

    def update_light_output_85(self, lout):
        light_output = set_light_output_t()
        light_output.nlights = 6
        light_output.lout = []
        for ind in range(0,light_output.nlights):
            logger.info("Setting light " + str(ind) + " to 85 %")
            light_output.lout.append(85)
            self.lightOutputs[ind].blockSignals(True)
            self.lightOutputs[ind].setValue(85)
            self.lightOutputs[ind].blockSignals(False)
        #light_output.lout = [lout for dim0 in range(0, light_output.nlights)]
        self.lcm_manager.lc.publish('EYERIS_LIGHT_OUTPUT', light_output.encode())

    def update_light_output(self, lout):
        light_output = set_light_output_t()
        light_output.nlights = 6
        light_output.lout = []
        for ind in range(0,light_output.nlights):
            lout = self.lightOutputs[ind].value()
            logger.info("Setting light " + str(ind) + " to " + str(lout) + " %")
            light_output.lout.append(lout)
        #light_output.lout = [lout for dim0 in range(0, light_output.nlights)]
        self.lcm_manager.lc.publish('EYERIS_LIGHT_OUTPUT', light_output.encode())

    def plot_update(self, plot, data, vals):

        plot.clear()
        for i in range(0, len(data)):
            if len(data[i]) > self.plot_history:
                data[i].popleft()
            data[i].append(vals[i])
            plot.plot(list(data[i]))

    def update_sensor(self, indicators, values, limits=[25, 35, 45]):

        for i in range(0, len(indicators)):
            if values[i] < limits[0]:
                indicators[i].setStyleSheet('color: #007bff')
            elif values[i] < limits[1]:
                indicators[i].setStyleSheet('color: #ffc107')
            else:
                indicators[i].setStyleSheet('color: #dc3545')

            indicators[i].display(values[i])

    def update_status(self, status):

        # Write to the log file
        self.data_logger.write_log(copy.deepcopy(status))

        self.update_sensor(self.tempIndicators, status.temperature, [25, 35, 45])
        self.update_sensor(self.humIndicators, status.humidity, [10, 20, 35])
        self.update_sensor(self.pressIndicators, status.pressure, [1000000, 1000000, 1000000])

        light_output = status.current[0]/1000.0

        #if self.last_light_output is not None:
        #    if light_output - self.last_light_output < -0.2:
        #        self.update_light_output(self.ui.lightOutputSpinBox.value())
        #
        #self.last_light_output = light_output

        self.ui.lightPowerIndicator.display(status.power[0]/1000.0)
        self.ui.systemPowerIndicator.display(status.power[1]/1000.0)
        self.ui.lightCurrentIndicator.display(status.current[0])
        self.ui.systemCurrentIndicator.display(status.current[1])
        self.ui.zoomIndicator.display(status.focal_length)
        self.ui.focusIndicator.display(status.focal_distance)
        self.ui.irisIndicator.display(status.aperture)
        self.relay_list = list(status.relays)
        self.ui.relay1Indicator.setChecked(self.relay_list[0])
        self.ui.relay2Indicator.setChecked(self.relay_list[1])
        self.ui.relay3Indicator.setChecked(self.relay_list[2])
        self.ui.relay4Indicator.setChecked(self.relay_list[3])

        # update the buttons
        if self.relay_list[0]:
            self.ui.cameraButton.setChecked(True)
        if self.relay_list[2] and self.relay_list[2]:
            self.ui.lightsButton.setChecked(True)

        # update charts
        self.plot_update(self.ui.temperaturePlot, self.temperatures, status.temperature)
        self.plot_update(self.ui.humidityPlot, self.humidities, status.humidity)
        self.plot_update(self.ui.pressurePlot, self.pressures, status.pressure)




    def set_gui_style(self):
        # setup stylesheet
        # set the environment variable to use a specific wrapper
        # it can be set to PyQt, PyQt5, PySide or PySide2 (not implemented yet)
        os.environ['PYQTGRAPH_QT_LIB'] = 'PyQt5'
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api=os.environ['PYQTGRAPH_QT_LIB']))



if __name__ == "__main__":

    # create the Qt application
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("EyeRIS-Control")

    # create the main window
    try:
        main = MainWindow(sys.argv)
        main.show()
    except Exception as e:
        print(e)
        sys.exit(1)
    # exit the app after the window is closed
    sys.exit(app.exec_())
