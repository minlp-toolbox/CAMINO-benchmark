import pandas as pd
from sys import argv
import os


if len(argv) != 2:
    print("Usage: python get_minlp_instances.py <path/to/minlplib/instances/csv>")
    exit(1)

filepath = argv[1]
dirpath = os.path.dirname(argv[1])

instance_df = pd.read_csv(filepath, sep=";")
instance_df = instance_df.loc[(instance_df['probtype'] == "MINLP") | (instance_df['probtype'] == "MBNLP")]

mask = ((instance_df["objsense"] == "min") | (instance_df["objsense"] == "max")) & (instance_df["formats"].str.contains("'nl'"))
convex_df = instance_df.loc[mask & (instance_df["convex"] == True)].copy(deep=True)
convex_df = convex_df[["name", "primalbound", "dualbound", "objsense"]]
nonconvex_df = instance_df.loc[mask & (instance_df["convex"] == False)].copy(deep=True)
nonconvex_df = nonconvex_df[["name", "primalbound", "dualbound", "objsense"]]

convex_df.set_index("name", inplace=True)
nonconvex_df.set_index("name", inplace=True)

convex_df.to_csv(os.path.join(dirpath, "convex_set_full.csv"))
nonconvex_df.to_csv(os.path.join(dirpath, "nonconvex_set_full.csv"))

print(f"csv with convex instances saved at {os.path.join(dirpath, 'convex_set_full.csv')}")
print(f"csv with nonconvex instances saved at {os.path.join(dirpath, 'nonconvex_set_full.csv')}")


