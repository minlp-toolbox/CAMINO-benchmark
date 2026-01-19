# This file is part of camino-benchmark
# Copyright (C) 2025  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later

import os
from sys import argv
from matplotlib import colors, lines
import numpy as np
import pandas as pd

LINESTYLES = [*lines.lineStyles.keys()][:4] * 2
MCOLORS = [*colors.TABLEAU_COLORS.keys()]

def to_float(val):
    """Convert to float."""
    if type(val) == str:
        if ("Objective" in val) or ("feasible" in val) or ("Error" in val) or ("Calling" in val) or ("g_val" in val) or ("CRASH" in val) or ("FAILED" in val) or ("empty" in val) or ("basic_string" in val) or ("No objective" in val) or ("Suffix values" in val) or ("for indices" in val) or ("has no attribute" in val):
            return np.inf
        elif val == "-inf":
            return np.inf
        elif val == "NAN":
            return np.inf
        else:
            val = float(val)
            if val > 1e20:
                return np.inf
            else:
                return float(val)
    else:
        return float(val)

def clip_keeping_inf(val):
    if (val > 300) and (val != np.inf):
        return 300
    else:
        return val

TIME_LIMIT = 300

data = pd.read_csv(argv[1])
key = argv[2]
SAVE_DIRECTORY = os.path.dirname(argv[1])


calc_time_cols = ["cvx_bonmin.calc_time", "cvx_sbmiqp.calc_time", "cvx_sbmiqp_ee.calc_time", "cvx_sbmilp.calc_time", "cvx_shot.calctime"]
total_time_df = data[["name"] + calc_time_cols]
total_time_df[calc_time_cols] = data[calc_time_cols].map(to_float)
total_time_df.rename(columns={"cvx_bonmin.calc_time": "bonmin",
                              "cvx_sbmiqp.calc_time": "sbmiqp",
                              "cvx_sbmiqp_ee.calc_time": "sbmiqp-ee",
                              "cvx_sbmilp.calc_time": "sbmilp",
                              "cvx_shot.calctime": "shot"},
                              inplace=True)
updated_time_cols = total_time_df.columns.tolist()[1:]
total_time_df[updated_time_cols] = total_time_df[updated_time_cols].map(clip_keeping_inf)

mask = (total_time_df["sbmiqp"] > 5) & total_time_df["sbmiqp"].notna()
df_mask = total_time_df[mask]
print(f"Original instances : {len(total_time_df)}")
print(f"Kept (sbmiqp >5s) : {len(df_mask)}")
print(f"Instances where sbmiqp >5s : {df_mask['name'].tolist()}")

mask1 = (total_time_df["sbmiqp"] < total_time_df["shot"])
df_mask1 = total_time_df[mask1]
print(f"\nInstances where sbmiqp faster than shot : {df_mask1['name'].tolist()}")

mask2 = (total_time_df["bonmin"] < total_time_df["shot"]) & (total_time_df["bonmin"] < total_time_df["sbmiqp"])
df_mask2 = total_time_df[mask2]
print(f"\nInstances where bonmin is faster than shot & sbmiqp : {df_mask2['name'].tolist()}")

mask3 = (total_time_df["sbmiqp"] > 5) & (total_time_df["sbmilp"] < total_time_df["sbmiqp"])
df_mask3 = total_time_df[mask3]
print(f"\nInstances where sbmilp is faster than sbmiqp : {df_mask3['name'].tolist()}")

mask4 = (total_time_df["sbmilp"] < total_time_df["sbmiqp"]) & (total_time_df["sbmilp"] < total_time_df["shot"])
df_mask4 = total_time_df[mask4]
print(f"\nInstances where sbmilp is faster than shot & sbmiqp : {df_mask4['name'].tolist()}")
