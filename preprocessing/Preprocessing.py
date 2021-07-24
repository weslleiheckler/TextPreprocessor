from multiprocessing import Pool, Process, Queue
import time
import numpy as np
import pandas as pd
import re, string, inflect
from textblob import Word
from wordsegment import load, segment
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize
import contractions

class Preprocessing():

    def __init__(self, pp_config, dict_df, log) -> None:
        self._pp_config = pp_config
        self._dict_df = dict_df
        self._log = log

    @property
    def dict_df(self):
        return self._dict_df

    def remove_line_break(self, df) -> pd.DataFrame:
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda w: str(w).replace('\n',' '))

        return df

    def expand_contractions(self, df) -> pd.DataFrame:
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda w: contractions.fix(w))

        return df

    def remove_special_characters(self, df) -> pd.DataFrame:
        # remove quotes (&quot)
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda w: str(w).replace('&quot',''))
        
        # maintain only characters from 'a to z' (upper and lower case) and numbers
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda w: ' '.join(re.sub('[^a-zA-Z0-9]+', ' ', w).split()))

        return df 

    def maintain_only_letters(self, df) -> pd.DataFrame:
        # maintain only characters from 'a to z' (upper and lower case)
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda w: ' '.join(re.sub('[^A-Za-z]+', ' ', w).split()))

        return df

    def remove_repeated_characters(self, df) -> pd.DataFrame:
        # remove characters repeated more than two times (e.g. 'missss' to 'miss')
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda w: ''.join(re.compile(r'(.)\1{2,}').sub(r'\1\1', w)))

        return df

    def spell_check(self, df) -> pd.DataFrame:
        # check the spelling of each word
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: ' '.join([Word(word).spellcheck()[0][0] for word in x.split()]))
        
        return df

    def remove_punctuation(self, df) -> pd.DataFrame:
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))

        return df

    def remove_stop_words(self, df) -> pd.DataFrame:
        nltk.download('stopwords')
        stops = stopwords.words('english')

        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stops)]))

        return df

    def lower_case(self, df):
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: x.lower())

        return df

    def upper_case(self, df) -> pd.DataFrame:
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: x.upper())

        return df

    def numbers_to_words(self, df) -> pd.DataFrame:
        p = inflect.engine()

        # transform numeric characters into words
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: ' '.join([p.number_to_words(word) if word.isdigit() else word for word in x.split()]))

        return df

    def segment_words(self, df):
        load()

        # segment combined words, such in the case of hashtags 
        # e.g. #word1word2 to #word1 word2
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: ' '.join(segment(x)))

        return df

    def lemmatization(self, df) -> pd.DataFrame:
        lemmatizer = WordNetLemmatizer()
        
        # get the lemma for each word
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: ' '.join([lemmatizer.lemmatize(word, pos='v') for word in x.split()]))

        return df

    def stemming(self, df) -> pd.DataFrame:
        nltk.download('punkt')
        stemmer = PorterStemmer()

        # get the stem for each word
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: ' '.join([stemmer.stem(word) for word in word_tokenize(x)]))

        return df

    def remove_mentions(self, df) -> pd.DataFrame:
        pattern = r'(?:@[\w_]+)'
        
        # remove mentions (e.g. @user)
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: ''.join(re.sub(pattern, '', x)))

        return df

    def remove_links(self, df) -> pd.DataFrame:
        pattern = r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+'

        # remove links (e.g. https://twitter.com/home)
        df['text_preprocessed'] = df['text_preprocessed'].apply(lambda x: ''.join(re.sub(pattern, '', x)))

        return df

    def parallelize_apply(self, df, function_name, n_cores) -> pd.DataFrame:
        # find the function     
        func = getattr(self, function_name)

        # split the dataframe in 'n_cores' parts
        df_split = np.array_split(df, n_cores)

        # create a pool of processes
        pool = Pool(n_cores)
             
        # apply the function and concatenate the divided dataframes
        df = pd.concat(pool.map(func, df_split))
        pool.close()
        pool.join()

        return df

    def preprocessing_manager(self, key, df, n_cores, queue) -> None:
        # create a column for text preprocessing
        # the original text will be maintained in the original column
        # the preprocessed text will be saved in the new column
        df_preprocessed = df
        df_preprocessed['text_preprocessed'] = df_preprocessed['text']

        # call functions for preprocessing according to the order in the preprocessing.cfg file
        for k, value in self._pp_config.dict_functions.items():
            if(value == 'Yes'):
                try:
                    self._log.user_message('Applying function ' + k, True)
                    df_preprocessed = self.parallelize_apply(df_preprocessed, k, n_cores)
                except:
                    self._log.exception('Fail to apply the preprocessing function \'' + k + '\' into the dataframe \'' + key + '\'.')

        # create a dictionary 
        dict = {key: df_preprocessed}

        # put the dictionary in the queue
        queue.put(dict)

    def preprocessing(self) -> None:
        start_time_pp = time.time()
        
        # get the number of cores from the configuration
        n_cores = self._pp_config.n_cores

        # configure the queue
        queue_preprocessing = Queue()

        # for each dataframe, create a process for preprocessing
        # each dataframe may be preprocessed with n cores
        processes = [Process(target=self.preprocessing_manager, args=(key, df, n_cores, queue_preprocessing)) for key, df in self._dict_df.items()]

        # start the processes
        for p in processes:
            p.start()

        # update the original dictionary
        for _ in processes:
            dict = queue_preprocessing.get()
            k = list(dict.keys())[0] # get the first (unique) key from the dictionary
            df_processed = dict[k] # get the dataframe
            self._dict_df[k] = df_processed

        # wait the processes
        for p in processes:
            p.join()

        final_time_pp = time.time() - start_time_pp
        self._log.timer_message('Preprocessing Time', str(final_time_pp) + ' seconds.')