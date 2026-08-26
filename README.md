# BioProEV 
*Biologically-relevant imputation of missing values in Proteomic analyses of Extracellular Vesicles*

BioProEV is a pipeline developed to handling missing values in proteomic data of extracellular vesicles (EVs). It (i) categorizes proteins using missing value data and (ii) uses machine learning to impute biologically relevant missing values. For the imputation step, it uses a Random Forest (RF) algorithm.

It categorizes the variables applying three conditions:

1. to reduce the risk of overfitting, any variable (i.e. a given protein) in which more than half of the values were missing is excluded from the dataset;
2. when all values in a variable are missing in one population, it is possible they are not missing randomly but due to protein absence/low expression in one of the EV populations; 
when this type of MNAR missing values (i.e. the type in which one population is different from another) is significantly enriched in the dataset, this is considered as biologically meaningful, and then the lowest possible value of “1” is imputed to replace these values in order to retain the biological differences; 
3. in all other cases, missing values are handled using a random forest imputation algorithm.

## Limitations

The user can adjust the percentage of missing values, as well as the number of samples. However, BioProEV is limited to two populations with the same, and small, number of samples, and cannot differentiate between missing values (NaN) configurations across samples, e.g. FBS-EVs = (NaN, NaN, NaN) and milk-EVs = (3, 2, NaN) is the same as FBS-EVs = (NaN, 2, NaN) and milk-EVs = (5, NaN, NaN), that is, four missing values in both cases. 

## Requirements

BioProEV was developed and tested with Python 3.12; other versions may work but are untested.

<br>

The package has been developed with the following Python library versions:

Numpy 2.2.1

Pandas 2.2.3

Scikit-learn 1.5.1

Matplotlib 3.2.1

<br>

BioProEV uses the random forest algorithm MissForest [1,2]:

MissForest v1.0.0 – released on 8 August 2024. 

## Installation

There are two code scripts to run BioProEV. For both, all arguments following the script name must be provided by the user (“data_file” to “file_name).

<br>

* missing_data_filtering.py

<br>

python3.12  missing_data_filtering.py data_file  sheet  gene_column  sample_column#1  sample_column#2 threshold   file_path   file_name

<br>

where:

```text
data_file          : File with the raw dataset (in .xlsx)
sheet              : Number of the file sheet with the dataset
gene_column        : Number of the column with gene IDs
sample_column#1    : Number of the column with the first sample data
sample_column#2    : Number of the column with the last sample data + 1 (e.g. column 12, so sample_column#2 = 13)
threshold          : Threshold for deleting most missing data variables (e.g. deletion of variables with more than 50 % of missing values, use 0.6)*
file_path 	       : Path to the folder where you will store the output file
file_name 		     : Name of the output file
```

&nbsp;&nbsp;\* check the outcome datatable for the threshold, it usually works best with rounded values (i.e. 0.6, not 0.63), also the decimals will depend on the number of samples.

* 
