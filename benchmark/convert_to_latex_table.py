# This file is part of camino-benchmark
# Copyright (C) 2025  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later

from sys import argv
import pandas as pd
import os
import numpy as np
import re


def to_float(val):
    """Convert to float."""
    if type(val) == str:
        if (
            ("Objective" in val)
            or ("feasible" in val)
            or ("Error" in val)
            or ("Calling" in val)
            or ("g_val" in val)
            or ("CRASH" in val)
            or ("FAILED" in val)
            or ("empty" in val)
            or ("basic_string" in val)
            or ("No objective" in val)
            or ("Suffix values" in val)
            or ("for indices" in val)
            or ("has no attribute" in val)
        ):
            return np.inf
        elif val == "-inf" or val == "-Infinity":
            return np.inf
        elif val == "NAN":
            return np.inf
        elif val == "0":
            return np.inf
        else:
            val = float(val)
            if abs(val) > 1e20:
                return np.inf
            else:
                return float(val)
    else:
        if abs(val) > 1e20:
            return np.inf
        return float(val)


TIME_LIMIT = 300

if __name__ == "__main__":

    if len(argv) != 4:
        print(
            "Usage: python convert_to_latex_table.py <data_file.csv> <key> <solve_time>"
        )
        print("key: cvx or noncvx")
        print("solve_time: solvetime or totaltime")
        exit(1)

    data = pd.read_csv(argv[1])
    SAVE_DIRECTORY = os.path.dirname(argv[1])
    key = argv[2]
    assert key == "cvx" or key == "noncvx"
    solve_time = argv[3]
    assert solve_time == "solvetime" or solve_time == "totaltime"

    solvers = [
        f"{key}_bonmin",
        f"{key}_gurobi",
        f"{key}_scip",
        f"{key}_shot",
        f"{key}_sbmiqp",
        f"{key}_sbmiqp_ee",
    ]
    solver_names = [
        "Bonmin",
        "Gurobi",
        "SCIP",
        "SHOT",
        "S-B-MIQP",
        "S-B-MIQP-ee",
    ]
    total_entries = data.shape[0]

    # Some data cleaning
    solvers_obj = [f"{solver}.obj" for solver in solvers]
    solvers_calctime = [solver + ".calc_time" for solver in solvers]
    if solve_time == "solvetime":
        for i in range(len(solvers_calctime)):
            if "sbmiqp" in solvers_calctime[i]:
                solvers_calctime[i] = solvers_calctime[i].split(".")[0] + ".solver_time"

    data[solvers_calctime] = data[solvers_calctime].map(to_float)
    data[solvers_obj] = data[solvers_obj].map(to_float)

    data["min.calctime"] = np.min(data[solvers_calctime], axis=1)
    data.set_index("name", inplace=True)

    for solver in solvers:
        if "shot" in solver:
            data.loc[data[f"{solver}.obj"] == np.inf, f"{solver}.calc_time"] = np.inf
        if "gurobi" in solver or "scip" in solver:
            mask = (data[f"{solver}.obj"].abs() > 1e10) | (data[f"{solver}.obj"] == 0)
            data.loc[mask, f"{solver}.calc_time"] = np.inf
            data.loc[mask, f"{solver}.obj"] = np.inf
    # clipping to 300 preserving inf
    cols = solvers_calctime + ["min.calctime"]
    mask = (data[cols] > 300) & np.isfinite(data[cols])
    data.loc[:, cols] = data[cols].mask(mask, 300)

    # Take only the columns you want to show
    df = data[solvers_obj + solvers_calctime].copy()

    # Build a MultiIndex for the columns: (solver, metric)
    def split_col(col: str, key: str):
        # matches e.g. "noncvx_bonmin.obj" or "noncvx_sbmiqp_ee.calc_time"
        if key == "cvx":
            m = re.match(r"cvx_(.+)\.(obj|calc_time)", col)
        else:
            m = re.match(r"noncvx_(.+)\.(obj|calc_time)", col)
        solver = m.group(1)
        metric = "Objective" if m.group(2) == "obj" else "Wall time"
        return solver, metric

    breakpoint()
    tuples = [split_col(c, key) for c in df.columns]
    df.columns = pd.MultiIndex.from_tuples(tuples, names=["solver", "metric"])

    # Optionally order columns so each solver has (objective, calc time)
    df = df.sort_index(axis=1, level=0)

    # Desired display order and names
    order = ["Bonmin", "Gurobi", "SCIP", "SHOT", "S-B-MIQP", "S-B-MIQP-ee"]

    # Map the “raw” solver keys to the display names
    raw_to_display = {
        "bonmin": "Bonmin",
        "gurobi": "Gurobi",
        "scip": "SCIP",
        "shot": "SHOT",
        "sbmiqp": "S-B-MIQP",
        "sbmiqp_ee": "S-B-MIQP-ee",
    }

    # 1) Rename level‑0 (solver) of the MultiIndex
    df.columns = df.columns.set_levels(
        [raw_to_display.get(s, s) for s in df.columns.levels[0]], level=0
    )

    # 2) Reorder the columns by solver, keeping the metric order
    new_cols = pd.MultiIndex.from_product([order, ["Objective", "Wall time"]])
    df = df.reindex(new_cols, axis=1)
    df.replace(np.inf, np.nan, inplace=True)

    # Export to LaTeX with multicolumn header; use longtable if you like
    latex = df.to_latex(
        buf=f"results/{key}_mc_table.tex",
        longtable=True,  # keeps your longtable environment
        multicolumn=True,
        multicolumn_format="c",  # center the top headers
        escape=False,  # keep solver names as-is
        index=True,  # keep the instance name index
        float_format="%.3g",  # tweak formatting as you wish
    )

    print(latex)
