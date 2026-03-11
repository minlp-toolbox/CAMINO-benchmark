import pandas as pd
import numpy as np
from sys import argv
from os import path
import csv

if len(argv) <= 3:
    print("Usage: output dataset-csv csvfiles")
    exit(0)

csv_out = argv[1]
dataset = argv[2]
other_csvs = argv[3:]
if path.exists(csv_out):
    raise Exception(f"CSV already exists: {csv_out}")

# 1. Read the main dataset
df_merged = pd.read_csv(dataset)

# 2. Iterate through other CSVs and merge them one by one
for f in other_csvs:
    if path.exists(f):
        # Read the current file
        df_current = pd.read_csv(f)
        df_current["path"] = df_current["path"].map(lambda x: x.split('.')[0])

        # --- Fix columns for failed rows ---
        # Identify rows where 'obj' is -inf
        is_failed = df_current['obj'] == float('-inf')

        if is_failed.any():
            # Set 'obj' to inf for these rows
            df_current.loc[is_failed, 'obj'] = np.inf

            # Set the rest of the row (excluding 'path' which is needed for merge) to NaN
            # Columns are: index(id)=0, path=1, obj=2, dual_obj=3...
            # We select columns starting from index 3 ('dual_obj')
            cols_to_nan = df_current.columns[3:]
            df_current.loc[is_failed, cols_to_nan] = np.nan


        # Rename columns starting from index 2 (skipping 'id' and 'path')
        # df_current.columns[2:] selects the 3rd column onwards
        cols_prefix = f.split('/')[-1].split('.')[0]
        cols_to_rename = {col: f"{cols_prefix}.{col}" for col in df_current.columns[2:]}
        df_current = df_current.rename(columns=cols_to_rename)
        # 1. Drop the 'id' column, as we don't need it in the final merged table
        df_current = df_current.drop(columns=['id'])

        # 2. Set 'path' as the index. We will use this to merge,
        # but it won't be added as a column in the final result.
        df_current = df_current.set_index('path')

        # 3. Merge. We match df_merged['name'] with df_current's index ('path').
        # Since 'path' is no longer a column in df_current, no 'path_x'/'path_y' are created.
        df_merged = pd.merge(df_merged, df_current, how='left', left_on='name', right_index=True)
    else:
        print(f"Warning: File not found: {f}")

# 3. Post-processing: Flip signs for maximization problems
#    for specific solvers (sbmiqp, sbmiqp_ee, bonmin)
obj_cols = [col for col in df_merged.columns.tolist() if "obj" in col]
target_solvers = ['sbmiqp', 'sbmiqp_ee', 'bonmin']
obj_cols = [col for col in obj_cols if 'sbmiqp' in col or 'sbmiqp_ee' in col or 'bonmin' in col]

# Create a mask where objsense is 'max'
mask_max = df_merged['objsense'] == 'max'
df_merged.loc[mask_max, obj_cols] *= -1

# Fill nan in cols obj and dualobj with inf
obj_cols = [col for col in df_merged.columns.tolist() if "obj" in col]
df_merged[obj_cols] = df_merged[obj_cols].fillna(np.inf)

# 4. Set 'name' as the index
df_merged = df_merged.set_index('name')

# 5. Save the output
df_merged.to_csv(csv_out)
