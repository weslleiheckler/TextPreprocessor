import pandas as pd
import glob

class Read():

    def __init__(self, log) -> None:
        self._log = log
        self._dict_df = {}

    @property
    def dict_df(self):
        return self._dict_df

    def read_data(self) -> pd.DataFrame:
        directoryPath = 'data_in\\'

        for file_name in glob.glob(directoryPath + '*.csv'):
            self._log.user_message('Reading ' + file_name)
            df = pd.read_csv(file_name)
            name = file_name.split('\\')[-1] # remove directory
            name = name.split('.')[0] # remove file extension
            self._dict_df[name] = df