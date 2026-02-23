# This file is part of camino-benchmark
# Copyright (C) 2025  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later


from sys import argv
from math import sqrt
from matplotlib import pyplot as plt
from matplotlib import lines
from matplotlib import colors
import matplotlib
import pandas as pd
import numpy as np
import os
from datetime import datetime


LINESTYLES = [*lines.lineStyles.keys()][:4] * 2
MCOLORS = [*colors.TABLEAU_COLORS.keys()]


def latexify(fig_width=None, fig_height=None):
    """
    Set up matplotlib's RC params for LaTeX plotting.

    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """
    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf
    if fig_width is None:
        fig_width = 5  # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5) - 1.0) / 2.0  # Aesthetic ratio
        fig_height = fig_width * golden_mean  # height in inches

    params = {
        # "backend": "ps",
        "text.latex.preamble": r"\usepackage{gensymb} \usepackage{amsmath}",
        "axes.labelsize": 8,  # fontsize for x and y labels (was 8)
        "axes.titlesize": 8,
        "lines.linewidth": 1,
        "legend.fontsize": 8,  # was 8
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "text.usetex": True,
        "figure.figsize": [fig_width, fig_height],
        "font.family": "serif",
        "figure.subplot.bottom": 0.15,
        "figure.subplot.top": 0.98,
        "figure.subplot.right": 0.95,
        "figure.subplot.left": 0.11,
        "legend.loc": 'lower right',
    }

    matplotlib.rcParams.update(params)

def compute_ratio(val_min, val_ref, corr=True):
    """Compute ratio."""
    ratios = []
    for imin, jval in zip(val_min, val_ref):
        imin, jval = float(imin), float(jval)
        if corr and imin < 1.0:
            corr = - imin + 1.0
            imin += corr
            jval += corr
        if np.isnan(jval):
            ratios.append(np.inf)
        else:
            if imin==0:
                ratios.append(np.nan)
            else:
                ratios.append(max(jval / imin, 1.0))

    return ratios

def collect_bins_plot(values, name, style, color, min_val=None, max_val=None, ax=None):
    """Collect in bins."""
    values = values[values < 1e5]
    res = values.value_counts().sort_index().cumsum()
    keys = res.keys().to_list()
    values = res.values.tolist()
    if min_val is not None:
        keys = [min_val] + keys
        values = [0] + values

    if max_val is not None:
        keys.append(max_val)
        values.append(values[-1])

    print(name, values)
    if ax:
        ax.plot(keys, values, style, color=color, label=name)
    else:
        plt.plot(keys, values, style, color=color, label=name)

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

def create_performance_profile(df, solver_columns, problem_column=None, tau_max=10, num_points=100,
                              log_scale=True, name="perf_plot", title="title", legend_labels=[],
                              xlabel="Within this factor of the best", ylabel="Fraction of problems solved"):
    """
    Create a performance profile plot comparing multiple solvers with support for both
    positive and negative values, and properly handling infinite values.
    Assumes smaller values are better.

    Parameters:
    -----------
    df : pandas.DataFrame
        The DataFrame containing the results
    solver_columns : list of str
        List of column names containing the solver results to compare
    problem_column : str, optional
        Column name identifying the problems. If None, the index is used
    tau_max : float, default=10
        Maximum value of the performance ratio to display
    num_points : int, default=100
        Number of points to evaluate the cumulative distribution
    log_scale : bool, default=True
        Whether to use a logarithmic scale for the x-axis
    title : str, default="Performance Profile"
        Plot title
    xlabel : str, default="Performance ratio τ"
        X-axis label
    ylabel : str, default="Probability P(r_{p,s} ≤ τ)"
        Y-axis label
    Returns:
    --------
    fig, ax : matplotlib Figure and Axes objects
    """
    # Make a copy of the data to avoid modifying the original
    data = df.copy()

    # Use index as problem identifier if problem_column is not provided
    if problem_column is None:
        problems = data.index
    else:
        problems = data[problem_column].unique()
    n_problems = len(problems)
    n_solvers = len(solver_columns)
    # Initialize performance ratios matrix
    perf_ratios = np.full((n_problems, n_solvers), np.nan)
    # Process each problem
    for i, problem in enumerate(problems):
        if problem_column is None:
            problem_data = data.loc[problem, solver_columns]
            if isinstance(problem_data, pd.Series):
                problem_data = problem_data.to_frame().T
        else:
            problem_data = data[data[problem_column] == problem][solver_columns]

        # Extract values for all solvers for this problem
        values = []
        valid_solvers = []
        for j, solver in enumerate(solver_columns):
            if solver in problem_data.columns:
                val = problem_data[solver].iloc[0]
                # Filter out NaN and infinite values
                if pd.notna(val) and not np.isinf(val):
                    values.append(val)
                    valid_solvers.append(solver)

        # If no valid values, skip this problem
        if len(values) == 0:
            continue
        values = np.array(values)
        # Handle negative values by transforming to a positive scale while preserving order
        min_value = np.min(values)
        # If all values are negative or mix of negative and positive
        if min_value < 0:
            # Transform values to ensure the best performance is positive
            transformed_values = values - min_value + 1
            # Find the best (smallest) transformed value
            best_perf = np.min(transformed_values)
            # Calculate performance ratios using transformed values
            for idx, solver in enumerate(valid_solvers):
                # print(f"{transformed_values[idx]=}, {best_perf=}")
                solver_j = solver_columns.index(solver)
                perf_ratios[i, solver_j] = transformed_values[idx] / best_perf
        else:
            # For all positive values, use standard calculation
            best_perf = np.min(values)
            # Calculate performance ratios
            for idx, solver in enumerate(valid_solvers):
                solver_j = solver_columns.index(solver)
                # print(f"{values[idx]=}, {best_perf=}")
                perf_ratios[i, solver_j] = values[idx] / best_perf
        # Mark missing, invalid, or infinite values as infinity in performance ratio
        for j, solver in enumerate(solver_columns):
            if solver not in valid_solvers:
                perf_ratios[i, j] = np.inf

    # Create range of tau values (performance ratios)
    if log_scale:
        tau_values = np.logspace(0, np.log10(tau_max), num_points)
    else:
        tau_values = np.linspace(1, tau_max, num_points)

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(3, 2))

    # Plot performance profiles for each solver
    for j, solver in enumerate(solver_columns):
        # For each tau value, calculate the fraction of problems where the solver's
        # performance ratio is less than or equal to tau
        profile = [np.sum(perf_ratios[:, j] <= tau) / n_problems for tau in tau_values]
        ax.plot(tau_values, profile, marker='', label=legend_labels[j],
                color=MCOLORS[j], linestyle=LINESTYLES[j])

    # Configure the plot
    if log_scale:
        ax.set_xscale('log')
    ax.set_xlim(1, tau_max)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_yticks(np.linspace(0,1,6))
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # if title=="Objective":
    ax.legend(ncols=2, columnspacing=0.5, handlelength=1.2)

    ax.set_title(title)
    fig.subplots_adjust(left=0.16, bottom=0.17, top=0.9)
    # plt.tight_layout()
    plt.savefig(f"{SAVE_DIRECTORY}/{datetime.now().strftime('%m-%d')}_{name}.pdf", dpi=300, bbox_inches='tight', pad_inches=0.05,)

    return fig, ax

NONCVX_INSTANCES_WITH_CUT_CORRECTION = ['batch0812_nc', 'batch_nc', 'csched2a', 'ex1233', 'ex1243', 'ex1244', 'ex1252', 'ex1252a', 'gear2', 'gear3', 'heatexch_spec2', 'nvs05', 'nvs21', 'parallel', 'spring', 'supplychainp1_020306', 'supplychainr1_020306', 'supplychainr1_030510', 'wastepaper5', 'waterno2_02']

if __name__ == "__main__":

    if len(argv) != 4:
        print("Usage: python create_plot.py <data_file.csv> <key> <solve_time>")
        print("key: cvx or noncvx")
        print("solve_time: solvetime or totaltime")
        exit(1)

    latexify(6, 4)
    data = pd.read_csv(argv[1])
    SAVE_DIRECTORY = os.path.dirname(argv[1])
    key = argv[2]
    assert (key == "cvx" or key == "noncvx")
    total_entries = data.shape[0]
    solve_time = argv[3]
    assert (solve_time == "solvetime" or solve_time == "totaltime")

    # =================== standard comparison ===================
    # solvers = [f"{key}_shot", f"{key}_sbmiqp"]
    # solver_names = ["SHOT", "S-B-MIQP"]

    # solvers = [f"{key}_bonmin", f"{key}_shot", f"{key}_sbmiqp", f"{key}_sbmiqp_ee",]
    # solver_names = ["Bonmin", "SHOT", "S-B-MIQP", "S-B-MIQP-ee"]

    # =================== v0.1.4 - v.0.1.5 comparison ===================
    # solvers = [ f"{key}_shot", f"{key}_sbmiqp", f"{key}_sbmiqp_new", f"{key}_sbmiqp_ee", f"{key}_sbmiqp_ee_new",]
    # solver_names = ["SHOT", "S-B-MIQP", "S-B-MIQP-new", "S-B-MIQP-ee", "S-B-MIQP-ee-new",]

    # solvers = [f"{key}_shot", f"{key}_sbmiqp_new", f"{key}_sbmiqp_ee_new",]
    # solver_names = ["SHOT", "S-B-MIQP-new", "S-B-MIQP-ee-new",]

    # solvers = [f"{key}_shot", f"{key}_sbmiqp_new", f"{key}_sbmiqp",]
    # solver_names = ["SHOT", "S-B-MIQP-new", "S-B-MIQP",]

    # solvers = [f"{key}_sbmiqp_new", f"{key}_sbmiqp",]
    # solver_names = ["S-B-MIQP-new", "S-B-MIQP",]

    # solvers = [f"{key}_sbmiqp_ee_new", f"{key}_sbmiqp_ee",]
    # solver_names = ["S-B-MIQP-ee-new", "S-B-MIQP-ee",]

    # =================== amplpy comparison ===================
    solvers = [f"{key}_bonmin", f"{key}_shot", f"{key}_sbmiqp", f"{key}_sbmiqp_ee", f"{key}_scip", f"{key}_gurobi"]
    solver_names = ["Bonmin", "SHOT", "S-B-MIQP", "S-B-MIQP-ee", "SCIP", "Gurobi",]

    # =================== alpha comparison ===================
    # solvers = [f"{key}_sbmiqp_005", f"{key}_sbmiqp_025", f"{key}_sbmiqp_050", f"{key}_sbmiqp_075", f"{key}_sbmiqp_095",]
    # solver_names = [r"$\alpha=0.05$", r"$\alpha=0.25$", r"$\alpha=0.50$", r"$\alpha=0.75$", r"$\alpha=0.95$"]

    # =================== rho comparison ===================
    # solvers = [f"{key}_sbmiqp_rho_1", f"{key}_sbmiqp_rho_1_5", f"{key}_sbmiqp_rho_5", f"{key}_sbmiqp_rho_10", f"{key}_sbmiqp_rho_50",]
    # solver_names = [r"$\rho=1$", r"$\rho=1.5$", r"$\rho=5$", r"$\rho=10$", r"$\rho=50$"]
    # data = data.loc[data["name"].isin(NONCVX_INSTANCES_WITH_CUT_CORRECTION)]

    # ========================== END ==========================


    solvers_obj = [f"{solver}.obj" for solver in solvers]
    solvers_calctime = [solver + ".calc_time" for solver in solvers]
    if solve_time == "solvetime":
        solvers_calctime[2] = solvers[2] + ".solver_time"
        solvers_calctime[3] = solvers[3] + ".solver_time"

    data[solvers_calctime] = data[solvers_calctime].map(to_float)
    data[solvers_obj] = data[solvers_obj].map(to_float)
    data['min.calctime'] = np.min(data[solvers_calctime], axis=1)
    data.set_index("name", inplace=True)
    for solver in solvers:
        if "shot" in solver:
            data[f'{solver}.calc_time'][data[f'{solver}.obj'] == np.inf] = np.inf

    # clipping to 300 preserving inf
    cols = solvers_calctime + ["min.calctime"]
    mask = (data[cols] > 300) & np.isfinite(data[cols])
    data.loc[:, cols] = data[cols].mask(mask, 300)

    def rel_gap(primal, obj, tol=1e-2):
        with np.errstate(divide='ignore', invalid='ignore'):
            g = (obj-primal) / np.abs(primal)
        g[~np.isfinite(g)] = np.nan
        if tol is not None:
            tiny = np.abs(g) < tol
            g[tiny] = 0.0
        return g
    for s, ct in zip(solvers, solvers_calctime):
        mask = data[ct] == 300                     # rows where this solver timed out
        gap  = rel_gap(data['primalbound'], data[f'{s}.obj'])
        failed = data[ct] == np.inf
        print(f'{s}: \t\t success {total_entries-failed.sum()-mask.sum():3d} | fail {failed.sum():2d} | time-out {mask.sum():3d} , gap <1e-1 {(gap[mask]<1e-1).sum():2d}')


    # set to inf objective >1e8 <-1e8 and == 0 for gurobi and scip
    if len(solvers_obj) == 6:
        cols = solvers_obj[-2:]
        mask = (data[cols].abs() > 1e8) | (data[cols] == 0)
        data.loc[:, cols] = data[cols].mask(mask, np.inf)
        cols_tmp = solvers_calctime[-2:]
        mask1 = data[cols[0]] == np.inf
        mask2 = data[cols[1]] == np.inf
        data.loc[mask1, cols_tmp[0]] = np.inf
        data.loc[mask2, cols_tmp[1]] = np.inf

    # New plots:
    create_performance_profile(data, solvers_calctime, tau_max=10, name=f'{key}_calc_time_profile_nsol{len(solver_names)}_{solve_time}', title="Wall time", legend_labels=solver_names, log_scale=False)
    create_performance_profile(data, solvers_obj, tau_max=1.5, name=f'{key}_obj_profile_nsol{len(solver_names)}_{solve_time}', title="Objective", legend_labels=solver_names, log_scale=False)

    plt.show()