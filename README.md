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

python3.12 &nbsp;&nbsp;&nbsp;&nbsp; missing_data_filtering.py &nbsp;&nbsp;&nbsp;&nbsp; data_file &nbsp;&nbsp;&nbsp;&nbsp;  sheet &nbsp;&nbsp;&nbsp;&nbsp;  gene_column &nbsp;&nbsp;&nbsp;&nbsp; sample_column#1 &nbsp;&nbsp;&nbsp;&nbsp; sample_column#2 &nbsp;&nbsp;&nbsp;&nbsp; threshold &nbsp;&nbsp;&nbsp;&nbsp; file_path &nbsp;&nbsp;&nbsp;&nbsp; file_name

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
file_name 	  	   : Name of the output file
```
&nbsp;&nbsp;\* check the outcome datatable for the threshold, it usually works best with rounded values (i.e. 0.6, not 0.63), also the decimals will depend on the number of samples.

<br>
  
Example of command line:

python3.12 &nbsp;&nbsp;&nbsp;&nbsp; missing_data_filtering.py &nbsp;&nbsp;&nbsp;&nbsp; raw_dataset.xlsx &nbsp;&nbsp;&nbsp;&nbsp; 2 &nbsp;&nbsp;&nbsp;&nbsp; 2 &nbsp;&nbsp;&nbsp;&nbsp; 7 &nbsp;&nbsp;&nbsp;&nbsp; 13 &nbsp;&nbsp;&nbsp;&nbsp; 0.6 &nbsp;&nbsp;&nbsp;&nbsp; ./output_folder &nbsp;&nbsp;&nbsp;&nbsp; output_file

<br>

where 7 is the column of the first sample data and 12 is the last sample (12 + 1 = 13).

<br>

Note that the columns and sheets in Excel files starting count in 0 and the default file extension is .xlsx

<br>

The data output here is the handled data to be used for the imputation step with the next code. 

<br>

* random_forest_imputation.py

<br>

Once you have the filtered data output, the next code will impute the missing data using MissForest algorithm:

<br>

python3.12 &nbsp;&nbsp;&nbsp;&nbsp; random_forest_imputation.py &nbsp;&nbsp;&nbsp;&nbsp; data_file &nbsp;&nbsp;&nbsp;&nbsp; sheet &nbsp;&nbsp;&nbsp;&nbsp; file_path  &nbsp;&nbsp;&nbsp;&nbsp; file_name

<br>

where:
```text
data_file     : File with the filtered data (in .xlsx) from the previous code
file_path	  : Path to the folder where you will store the output file
file_name	  : Name of the output file
```
<br>

Example of command line:

python3.12 &nbsp;&nbsp;&nbsp;&nbsp; random_forest_imputation.py &nbsp;&nbsp;&nbsp;&nbsp; filtered_data.xlsx &nbsp;&nbsp;&nbsp;&nbsp; 2 &nbsp;&nbsp;&nbsp;&nbsp; ./output_folder &nbsp;&nbsp;&nbsp;&nbsp; output_file

Note that the Random Forest algorithm here uses the data matrix as sample x variables (i.e. rows x columns). In the output file from the filtering step (previous code script) it will be stored on the sheet 2.

| Gene      | Smpdl3b | Lamc1 | Bgn | Emilin1 | Pgam1 | G3bp1 |
| --------- | ------: | ----: | --: | ------: | ----: | ----: |
| Sample 01 |       9 |    81 |  64 |      80 |    10 |     4 |
| Sample 02 |      13 |   104 |  77 |      77 |    12 |     3 |
| Sample 03 |       7 |    82 |  82 |      92 |    13 |     6 |
| Sample 04 |      23 |    86 |  80 |      70 |    21 |    12 |
| Sample 05 |      16 |   100 | 124 |      73 |    26 |    15 |
| Sample 06 |      20 |   134 | 102 |      89 |    23 |     8 |

## Output
There will be an output file for each code:

* From missing_values_filtering.py: the output file will have four sheets containing “raw data”, “filtered data”, “transpose filtered data” and “missdata info”, where you will find information about the missing data.
    
* From random_forest_imputation.py: the output file will have two sheets containing “imputed data” and “transpose imputed data”.

## Authors
Pâmella Miranda --- pamella.mm@gmail 

Jose G. Marchan-Alvarez --- jose.marchan@ki.se 

Phillip Newton --- phillip.newton@ki.se 

## References
[1] Yuen, S. Y. H. (2024). yuenshingyan/MissForest: MissForest in Python – Arguably the best missing values imputation method. Version v1.0.0. doi:10.5281/zenodo.13368883. [Computer software].

[2] https://pypi.org/project/MissForest/

## Citation
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15345157.svg)](https://doi.org/10.5281/zenodo.15440849)

Miranda, P., Marchan Alvarez, J. G., & Newton, P. (2025). BioProEV - Biologically-relevant imputation of missing values in Proteomic analyses of Extracellular Vesicles. Zenodo. https://doi.org/10.5281/zenodo.15440849
