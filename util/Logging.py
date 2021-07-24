import logging

class Logging():

    def __init__(self, user_messages = False, timer_messages = False) -> None:
        logging.basicConfig(level = logging.NOTSET, format = '%(message)s')
        self._user_messages = user_messages
        self._timer_messages = timer_messages
    
    def warning(self, message) -> None:
        logging.warning('Warning: ' + message)

    def error(self, message) -> None:
        logging.error('Error:' + message)

    def exception(self, message) -> None:
        logging.exception('Exception: ' + message)

    def user_message(self, message, print_function = False) -> None:
        if(self._user_messages):
            if(print_function):
                print('Info: ' + message)
            else:
                logging.info('Info: ' + message)

    def timer_message(self, title, message) -> None:
        if(self._timer_messages):
            logging.info(title + ': ' + message)