
# ----------------------------------------------------------------------------------------------------------
#   Last modified: 26 August 2025
#
#   Missing data imputation
#
#   Random Forest (RF) algorithm --> MissForest (https://pypi.org/project/MissForest/)
#
#   Arguments:
#       data_file        : Dataset in .xlsx
#       sheet            : Sheet of interest (samples in rows & variables/genes in columns)
#       file_path        : Output directory
#       file_name        : Output file
#
#   Usage:
#       python3.12 random_forest_imputation.py data_file sheet file_path file_name 
#
#   Developed and tested with Python 3.12; other versions may work but are untested.
# ----------------------------------------------------------------------------------------------------------

import sys
import pandas as pd
# MissForest algorithm implementation: https://pypi.org/project/MissForest/
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from missforest import MissForest

data_file = sys.argv[1]     # Dataset
sheet = int(sys.argv[2])    # Sheet of interest (samples in rows & variables/genes in columns)
path_file = sys.argv[3]     # Path for output file --> e.g. ../file_path/
name_file = sys.argv[4]     # Output file --> e.g. output_file

# Dataset with missing values, that is, the filtered data
filtered_data = pd.read_excel(data_file, sheet_name=sheet) # Sheet reading starts at 0

# Prepare data for missing values imputation
# Samples in rows & variables/genes in columns
data_fillna = filtered_data
codes_samples = data_fillna.drop(data_fillna.columns[1:],axis=1) # Save sample codes
data_prepared_mvs = data_fillna.drop(data_fillna.columns[0],axis=1) # Save data
names_genes = data_prepared_mvs.columns # Save genes

# Random forest method
clf = RandomForestClassifier(n_jobs=-1)
rgr = RandomForestRegressor(n_jobs=-1)

imputer = MissForest(clf,rgr)
data_rf = imputer.fit_transform(data_prepared_mvs)

# Organise the final data
data_rf = pd.DataFrame(data_rf)
data_rf.columns = names_genes

data_imputed = pd.concat([codes_samples,data_rf], axis=1)
transpose_imputed = data_imputed.T

# Save the results
with pd.ExcelWriter(path_file+name_file+'.xlsx') as writer:
    transpose_imputed.to_excel(writer,sheet_name='imputed data',header=False)
    data_imputed.to_excel(writer,sheet_name='transpose imputed data',index=False)
