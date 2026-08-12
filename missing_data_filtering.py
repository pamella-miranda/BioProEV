# ----------------------------------------------------------------------------------------------------------
#   Last modified: 26 August 2025
#
#   Data extraction and missing data filtering
#
#   More than 50% of missing values (per variable/gene) --> deletion
#   One sample group (population) completely missing --> replace with value "1"
#   Remaining missing values --> imputation method
#
#   Arguments:
#       data_file        : Dataset in .xlsx
#       sheet            : Sheet of interest
#       gene_column      : Column of genes/proteins ids
#       sample_column#1  : Column with the first sample data
#       sample_column#2  : Column with the last sample data + 1, e.g. 12 + 1 = 13
#       threshold        : Percentage in decimals of missing values across all samples (per variable) 
#       file_path        : Output directory
#       file_name        : Output file
#
#   Usage:
#       python3.12 missing_data_filtering.py dataset sheet gene_column sample_column#1 sample_column#2 
#   threshold file_path file_name
#
#   Developed and tested with Python 3.12; other versions may work but are untested.
# ----------------------------------------------------------------------------------------------------------

import sys
import pandas as pd
import numpy as np
import scipy.stats as stats

# Copy-on-Write (CoW) for pandas 3.0
pd.options.mode.copy_on_write = True

data_file = sys.argv[1]                                         # Dataset
sheet = int(sys.argv[2])                                        # Sheet of interest
gene_column = int(sys.argv[3])                                  # Column of genes/proteins ids
cols_samples = list(range(int(sys.argv[4]), int(sys.argv[5])))  # Sample columns
threshold = float(sys.argv[6])                                  # Threshold (in decimals) of missing values per variable
path_file = sys.argv[7]                                         # Path for output file --> e.g. ../path_file/
name_file = sys.argv[8]                                         # Output file --> e.g. output_file.xlsx

# Join gene and sample columns
cols_samples.insert(0,gene_column)

# Specific dataset
data_input = pd.read_excel(data_file, sheet_name=sheet, usecols=cols_samples) # Sheet reading starts at 0

# Transpose data (samples in rows and variables/genes in columns)
data_extract = data_input.set_index(data_input.columns[0]).T # Header are the genes
data_extract = data_extract.rename_axis(data_input.columns[0]).reset_index() # Index are numbers
data_extract = data_extract.rename_axis(None, axis=1) # Exclude header for index
datatable = data_extract.iloc[:,1:] # Only the variables/genes columns

# Samples codes
samples_codes = data_input.columns[1:]
samples_codes = pd.DataFrame(samples_codes)

# Filter dataset
# Apply the conditions for missing values (mvs)
#------------------------------------------------------
# CONDITION 1
# Delete columns with more than 50% of missing values
#------------------------------------------------------
# Save variables with less or equal 50% of missing values
mvs_data = data_extract.loc[:,data_extract.isnull().mean() < threshold]
# Genes list with more than 50% of missing values
mvs_data_out = data_extract.loc[:,data_extract.isnull().mean() > threshold]
mvs_data_out = mvs_data_out.columns
mvs_data_out = pd.DataFrame(mvs_data_out)

# Handle the duplicate genes
data_for_check = mvs_data.set_index(mvs_data.columns[0]).T
data_for_check = data_for_check.rename_axis(mvs_data.columns[0]).reset_index()
data_for_check = data_for_check.rename_axis(None, axis=1)
duplicate_genes = data_for_check[data_for_check[data_for_check.columns[0]].duplicated(keep=False)]

#--------------------------------------------------------------------------------------------------------------
# If there are duplicates in the dataset
duplicates_extracted = []
gene_extracted = []

if len(duplicate_genes) > 0:
    duplicate_genes = duplicate_genes.reset_index()
    duplicate_genes = duplicate_genes.iloc[:,1:]
    duplicates = duplicate_genes.set_index(duplicate_genes.columns[0]).T
    duplicate_names = duplicates.columns[duplicates.columns.duplicated()].unique() #unique name for duplicates

    for n in duplicate_names:
        id_col = duplicate_genes.columns[0]
        id_gene = duplicate_genes.index[duplicate_genes[id_col] == n]
        duplicates_extracted.append(duplicate_genes.iloc[id_gene])

    # Compare the numbers of missing values to select the duplicate:
    # those with less missing values;
    # those with the highest abundance, when both duplicates have the same number of observed values;
    # observed values --> non-missing values
    for d in duplicates_extracted:
        id1 = d.iloc[0]
        id2 = d.iloc[1]
        id1_sum = id1.isnull().sum()
        id2_sum = id2.isnull().sum()
        if id1_sum == id2_sum:
            id1_sum_total = id1.iloc[1:].sum()
            id2_sum_total = id2.iloc[1:].sum()
            if id1_sum_total > id2_sum_total:
                gene_extracted.append(id1)
            elif id1_sum_total < id2_sum_total:
                gene_extracted.append(id2)
        elif id1_sum < id2_sum:
            gene_extracted.append(id1)
        elif id1_sum > id2_sum:
            gene_extracted.append(id2)

    gene_extracted = pd.DataFrame(gene_extracted)
    gene_extracted_to_data = gene_extracted.set_index(gene_extracted.columns[0]).T
    gene_extracted_to_data = gene_extracted_to_data.rename_axis(gene_extracted.columns[0]).reset_index()
    gene_extracted_to_data = gene_extracted_to_data.rename_axis(None, axis=1)
    gene_extracted_to_data = gene_extracted_to_data.iloc[:,1:]

    # Remove the duplicates from the filtered data
    data_for_check = mvs_data.set_index(mvs_data.columns[0]).T
    data_for_check = data_for_check.rename_axis(mvs_data.columns[0]).reset_index()
    data_for_check = data_for_check.rename_axis(None, axis=1)
    duplicates_columns = mvs_data.columns[mvs_data.columns.duplicated()]
    mvs_data.drop(columns=duplicates_columns, inplace=True)

    # Save together the data with no duplicates and the selected duplicates
    mvs_data = pd.concat([mvs_data,gene_extracted_to_data], axis=1, ignore_index=False)
#--------------------------------------------------------------------------------------------------------------

# Variables for the missing value conditions
# For example, group1=samples1,2,3 and group2=samples4,5,6
observed_data = [] # Genes with no missing values
mvs_half_distributed = [] # Genes with 50% of missing values distributed in both groups
mvs_half_one_group = [] # Genes with 50% of missing values in one group
mvs_imputation = [] # Genes for imputation step
mvs_replace_one = [] # Genes with all missing values in one group

# Only genes, no sample codes column
mvs_data_columns = mvs_data.iloc[:,1:]

# Collect the missing value conditions
for c in mvs_data_columns.columns:
    c_name = mvs_data[c].isnull()
    count = c_name.sum()
    c_name = c_name.to_numpy()
    split_c_name = np.array_split(c_name, 2)
    group1 = split_c_name[0]
    group2 = split_c_name[1]
    group1_count = np.count_nonzero(group1 == True)
    group2_count = np.count_nonzero(group2 == True)
    groups_sum = group1_count + group2_count
    if groups_sum == 0:
        observed_data.append(c)
    elif ((group1_count==len(group1)) & (group2_count==0)) | ((group1_count==0) & (group2_count==len(group2))):
        mvs_half_one_group.append(c)
    elif groups_sum == len(group1):
        mvs_half_distributed.append(c)
        mvs_imputation.append(c)
    else:
        mvs_imputation.append(c)

#-------------------------------------------------------------------------------------------
# CONDITION 2
# When all values in a variable are missing in one population and are significantly
# enriched in the dataset, it is considered as biologically meaningful, and then
# the lowest possible value of "1" is imputed in order to retain the biological differences
#-------------------------------------------------------------------------------------------
# Fisher's test for randomness of half of the missing values
# Contingency table
half_one_group = len(mvs_half_one_group)
half_distributed = len(mvs_half_distributed)
half_sum = half_one_group + half_distributed
half_ten_percent = round(half_sum*0.1)
half_ninety_percent = round(half_sum*0.9)

contingency_table = [[half_ten_percent, half_ninety_percent], [half_one_group, half_distributed]]

odd_ratio, p_value = stats.fisher_exact(contingency_table)

# Categorise variables/genes with half missing value count
if p_value < 0.05: # Statistically significant
    for a in mvs_data.columns:
        for b in mvs_half_one_group:
            if a == b:
                mvs_data.loc[:,a] = mvs_data[a].fillna(1)
                mvs_replace_one.append(a)
else:
    mvs_imputation = mvs_imputation + mvs_half_one_group

# Count of missing values and total amount of data
mvs_total = datatable.isnull().sum().sum() # Total amount of missing values
mvs_genes = datatable.isnull().sum() # Missing values for each gene
data_total = len(datatable.index) * len(datatable.columns) # Total amount of data
genes_total = len(data_extract.columns)-1 # Total amount of genes

# Percentage of missing values in total amount of data
data_total_percent = (mvs_total * 100)/data_total
data_total_percent = str(round(data_total_percent,1))
# Percentage of missing values for each gene
mvs_genes_percent = round((mvs_genes * 100)/6,1)
# Percentage of missing values for each sample
sampleset = data_extract.T # Table for samples
mvs_samples = sampleset.isnull().sum() # Missing values for each sample
mvs_samples_percent = round((mvs_samples * 100)/len(sampleset.index)) # Percentage for each sample

# Transform information into a dataframe
data_total = pd.DataFrame([data_total])
mvs_total = pd.DataFrame([mvs_total])
data_total_percent = pd.DataFrame([data_total_percent])
genes = pd.DataFrame(mvs_genes.index)
mvs_genes = mvs_genes.values
mvs_genes = pd.DataFrame(mvs_genes)
mvs_genes_percent = mvs_genes_percent.values
mvs_genes_percent = pd.DataFrame(mvs_genes_percent)
data_total_count = pd.DataFrame([genes_total])

# Percentage of each missing value condition
count_mvs_replace_one = round(((len(mvs_replace_one)*100)/genes_total),1)
count_mvs_imputation = round(((len(mvs_imputation)*100)/genes_total),1)
# Percentage of observed data
count_observed_data = round(((len(observed_data)*100)/genes_total),1)
# Percentage of genes with more than 50% of missing values
count_mvs_out = round(((len(mvs_data_out)*100)/genes_total),1)

# Count of filtered data, that is, below the missing values threshold
filtered_data_total = len(mvs_data.index) * (len(mvs_data.columns)-1) # Total amount of filtered data
mvs_filtered_data = mvs_data.isnull().sum().sum() # Missing values for total amount of filtered data
mvs_filtered_genes = mvs_data.isnull().sum() # Missing values for each gene
genes_total_count = len(mvs_data.columns)-1 # Total amount of genes
filtered_genes = pd.DataFrame(mvs_filtered_genes.index[1:]) # Genes
filtered_genes_mvs = mvs_filtered_genes.values[1:]
filtered_genes_mvs = pd.DataFrame(filtered_genes_mvs) # Missing values for each gene

# Percentage of missing values in total amount of filtered data
mvs_filtered_percent = round(((mvs_filtered_data*100)/filtered_data_total),1)
mvs_filtered_percent = str(round(mvs_filtered_percent,1))
# Percentage of missing values for each gene
filtered_genes_percent = round((mvs_filtered_genes * 100)/6,1)
# Percentage of missing values for each sample
filtered_samples = mvs_data.T
mvs_filtered_samples = filtered_samples.isnull().sum() # Missing values
filtered_samples_percent = round((mvs_filtered_samples * 100)/genes_total_count,1) # Percentage

# Transform information into a dataframe
mvs_replace_one = pd.DataFrame(mvs_replace_one)
mvs_imputation = pd.DataFrame(mvs_imputation)
observed_data = pd.DataFrame(observed_data)
count_observed_data = pd.DataFrame([count_observed_data])

count_mvs_replace_one = pd.DataFrame([count_mvs_replace_one])
count_mvs_imputation = pd.DataFrame([count_mvs_imputation])
count_mvs_out = pd.DataFrame([count_mvs_out])
filtered_data_total = pd.DataFrame([filtered_data_total])
mvs_filtered_data = pd.DataFrame([mvs_filtered_data])
mvs_filtered_percent = pd.DataFrame([mvs_filtered_percent])
genes_total_count = pd.DataFrame([genes_total_count])
mvs_filtered_genes = pd.DataFrame([mvs_filtered_genes])
filtered_genes_percent = filtered_genes_percent.values[1:]
filtered_genes_percent = pd.DataFrame(filtered_genes_percent)

count_mvs = pd.concat([observed_data,count_observed_data,mvs_replace_one,count_mvs_replace_one,mvs_imputation,count_mvs_imputation,
                       mvs_data_out,count_mvs_out,data_total,mvs_total,data_total_percent,
                       data_total_count,genes,mvs_genes,mvs_genes_percent,samples_codes,
                       mvs_samples,mvs_samples_percent,filtered_data_total,mvs_filtered_data,mvs_filtered_percent,
                       genes_total_count,filtered_genes,filtered_genes_mvs,filtered_genes_percent,
                       samples_codes,mvs_filtered_samples,filtered_samples_percent], axis=1)
count_mvs.columns = ['0 NaN', '0 NaN %','50% NaN (one group)','50% NaN (one group) %','NaN for imputation',
                     'NaN for imputation %', 'more than 50% NaN','more than 50% NaN %','Raw Data',
                     'Raw NaN Count','Raw NaN %','Total Genes','Genes',
                     'Gene NaN Count','Gene NaN %','Samples','Sample NaN Count',
                     'Sample NaN %','Final Data','Final NaN','Final NaN %',
                     'Final Genes','Genes','Final Gene NaN Count',
                     'Final NaN Count %','Samples','Final Sample NaN Count','Final NaN Count %']

# Save the results
with pd.ExcelWriter(path_file+name_file+'.xlsx') as writer:
    data_input.to_excel(writer,sheet_name='raw data',index=False)
    mvs_data.T.to_excel(writer,sheet_name='filtered data',header=False)
# Sheet to use for imputation: samples in rows and variables/genes in columns ('transpose filtered data')
    mvs_data.to_excel(writer,sheet_name='transpose filtered data',index=False)
    count_mvs.to_excel(writer,sheet_name='missdata info',index=False)
