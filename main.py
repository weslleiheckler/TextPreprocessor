from util import Logging as log
from preprocessing import PreprocessingConfiguration as pc
from preprocessing import Preprocessing as pp
from data_io import Read as rd
from data_io import Save as sv

class Main():

    def main():

        # create a logger
        logging = log.Logging(user_messages = True, timer_messages = True)

        # preprocessing configurations
        pp_config = pc.PreprocessingConfiguration(logging)
        pp_config.config()

        # read the data
        rd_data = rd.Read(logging)
        rd_data.read_data()

        # preprocess the data
        preprocessing = pp.Preprocessing(pp_config, rd_data.dict_df, logging)
        preprocessing.preprocessing()

        # save the data
        save = sv.Save(rd_data.dict_df, logging)
        save.save()

    if __name__ == "__main__":
        main()