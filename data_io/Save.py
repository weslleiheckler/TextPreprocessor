from multiprocessing import Process
import time

class Save():

    def __init__(self, dict_df, log) -> None:
        self._dict_df = dict_df
        self._log = log

    def save_csv(self, key, df) -> None:
        # get the path and file name
        path = 'data_out\\'
        name = key + '.csv'
        file_name = path + name

        # separator and encoding
        sep = ';'
        enc = 'utf-8'

        # save to csv
        self._log.user_message('Saving ' + file_name, True)
        df.to_csv(file_name, encoding = enc, sep = sep)

    def save(self) -> None:
        start_time_save = time.time()

        # for each dataframe in the dictionary, create a process for saving
        processes = [Process(target=self.save_csv, args=(key, df)) for key, df in self._dict_df.items()]

        # start the processes
        for p in processes:
            p.start()
        
        # wait the processes
        for p in processes:
            p.join()

        final_time_save = time.time() - start_time_save
        self._log.timer_message('Saving Time', str(final_time_save) + ' seconds.')