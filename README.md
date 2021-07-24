## Description of Text Preprocessor :star:

<p align="justify">
This tool preprocesses the text column from multiple datasets in a parallelized way. Each dataset is preprocessed in a different process and each process can create subprocesses for parallelizing the functions of preprocessing. It is possible to configure which functions will be applied in this task and the order in which the application occurs. The datasets must be structured in CSV files.
</p>

## Configurations :star:

<p align="justify">
Before executing the tool, some configurations are required:
</p>

- The dataframes (CSV files) must be placed in the "data_in" subdirectory. After preprocessing, the datasets will be saved in the "data_out" subdirectory;

- Each dataset must have a column named "text". The preprocessing will be performed in this column;

- The number of cores (n_cores) must be defined in the "preprocessing.cfg" file in the "config" subdirectory. This parameter defines the number of subprocesses for parallelizing the preprocessing of each dataset. The tool will split each dataset into "n_cores" parts and it will preprocess all parts in parallel. When "auto" (n_cores = auto), the tool will use all CPUs available;

- The preprocessing functions must be configured in the "preprocessing.cfg" file in the "config" subdirectory. The tool will execute all functions configured with the "Yes" value. It is worth noting that the functions will be performed considering the same order defined in the file. Moreover, it is possible to repeat functions as necessary. 