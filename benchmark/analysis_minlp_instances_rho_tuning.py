import pandas as pd
import numpy as np

def to_float(val):
    """Convert to float."""
    if type(val) == str:
        if ("Objective" in val) or ("feasible" in val) or ("Error" in val) or ("Calling" in val) or ("g_val" in val) or ("CRASH" in val) or ("FAILED" in val) or ("empty" in val) or ("basic_string" in val) or ("No objective" in val) or ("Suffix values" in val) or ("for indices" in val) or ("has no attribute" in val):
            return np.inf
        elif val == "-inf" or val=="-Infinity":
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
        if val == -np.inf:
            return np.inf
        return float(val)


data_df = pd.read_csv("results/26_03_06/noncvx_sbmiqp.csv")

data_df['obj'].map(to_float)
mask = abs(data_df.obj)==np.inf
data_df = (data_df[~mask]).copy(deep=True)

tmp = data_df['path'].tolist()
names = [word.split('.')[0] for word in tmp]
print(names)
