import configparser, os

class PreprocessingConfiguration():

    def __init__(self, log) -> None:
        self._n_cores = 0
        self._dict_functions = {}
        self._log = log

    @property
    def n_cores(self):
        return int(self._n_cores)

    @property
    def dict_functions(self):
        return self._dict_functions

    def config(self) -> None:
        
        # check whether the config file exists
        if not os.path.exists('config/preprocessing.cfg'): 
            self._log.error('Preprocessing configuration file not found. Verify whether the preprocessing.cfg file is in the config subdirectory.')
        else:
            # read the connection configurations in the ini file
            config = configparser.ConfigParser()
            config.read('config/preprocessing.cfg')

            # verify the Preprocessing section
            if 'Preprocessing' in config:
                try:
                    self._log.user_message('Configuring the preprocessing')

                    for param, value in config.items('Preprocessing'):
                        if(param == 'n_cores'):
                            # when n_cores = auto, all CPUs available will be used (os.cpu_count())
                            self._n_cores = os.cpu_count() if value == 'auto' else config['Preprocessing']['n_cores']
                        else:
                            self._dict_functions[param] = value
                except:
                    self._log.exception('Preprocessing keys not found or incorrect. Verify the Preprocessing section in the config file.')               
            else:
                self._log.error('Preprocessing section not found. Verify the Preprocessing section in the config file.')