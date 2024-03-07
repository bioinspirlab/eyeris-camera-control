import os
import logging
import datetime
from logger import get_file_logger

if __name__=="__main__":
    timestamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    filename = os.path.join('notes', 'EyeRIS-Control-' + timestamp + '.txt')

    LOG = get_file_logger(filename, file_level=logging.DEBUG, logger_name='EyeRIS-Op-Notes')

    user_input = ""

    while user_input.lower() != "exit":
        user_input = input("Notes > ")
        if user_input.lower != "" and user_input.lower != "exit":
            LOG.info(user_input)