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
        elif val == "-inf" or val=="-Infinity":
            return np.inf
        elif val == "NAN":
            return np.inf
        elif val == '0':
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

def create_performance_profile(df, solver_columns, ylim=(0, 1), problem_column=None, tau_max=10, num_points=100,
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
        if min_value <= 0:
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
        print(f"\n {solver=}, {profile[-1]}")
        ax.plot(tau_values, profile, marker='', label=legend_labels[j],
                color=MCOLORS[j], linestyle=LINESTYLES[j])

    # Configure the plot
    if log_scale:
        ax.set_xscale('log')
    ax.set_xlim(1, tau_max)
    if ylim[0]==0:
        ax.set_ylim(ylim[0], 1.05)
    else:
        ax.set_ylim(ylim)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_yticks(np.linspace(ylim[0],1,6))
    # ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # if title=="Objective":
    ax.legend(ncols=2, columnspacing=0.5, handlelength=1.2)

    ax.set_title(title)
    fig.subplots_adjust(left=0.16, bottom=0.17, top=0.9)
    # plt.tight_layout()
    plt.savefig(f"{SAVE_DIRECTORY}/{datetime.now().strftime('%m-%d')}_{name}.png", dpi=300, bbox_inches='tight', pad_inches=0.05,)

    return fig, ax

NONCVX_INSTANCES_WITH_CUT_CORRECTION = ['autocorr_bern20-05', 'autocorr_bern20-10', 'autocorr_bern20-15', 'autocorr_bern25-06', 'autocorr_bern25-13', 'autocorr_bern25-19', 'autocorr_bern25-25', 'autocorr_bern30-04', 'autocorr_bern30-08', 'autocorr_bern30-15', 'autocorr_bern30-23', 'autocorr_bern30-30', 'autocorr_bern35-04', 'autocorr_bern35-09', 'autocorr_bern35-18', 'autocorr_bern35-26', 'autocorr_bern35-35fix', 'autocorr_bern40-05', 'autocorr_bern40-10', 'autocorr_bern40-20', 'autocorr_bern40-30', 'autocorr_bern40-40', 'autocorr_bern45-05', 'autocorr_bern45-11', 'autocorr_bern45-23', 'autocorr_bern45-34', 'autocorr_bern45-45', 'autocorr_bern50-06', 'autocorr_bern50-13', 'autocorr_bern50-25', 'autocorr_bern50-38', 'autocorr_bern50-50', 'autocorr_bern55-06', 'autocorr_bern55-14', 'autocorr_bern55-28', 'autocorr_bern55-41', 'autocorr_bern55-55', 'autocorr_bern60-08', 'autocorr_bern60-15', 'autocorr_bern60-30', 'autocorr_bern60-45', 'autocorr_bern60-60', 'batch0812_nc', 'batch_nc', 'casctanks', 'cecil_13', 'chp_shorttermplan1a', 'contvar', 'csched1', 'csched1a', 'csched2', 'csched2a', 'deb10', 'deb6', 'deb7', 'deb8', 'deb9', 'eg_all_s', 'eg_disc2_s', 'eg_disc_s', 'eg_int_s', 'ex1221', 'ex1222', 'ex1224', 'ex1225', 'ex1226', 'ex1233', 'ex1243', 'ex1244', 'ex1252', 'ex1252a', 'ex3pb', 'feedtray', 'fin2bb', 'gastrans', 'gastrans040', 'gastrans135', 'gear4', 'ghg_1veh', 'ghg_2veh', 'ghg_3veh', 'gkocis', 'hadamard_4', 'hadamard_5', 'hadamard_6', 'hadamard_7', 'hadamard_8', 'heatexch_gen1', 'heatexch_spec1', 'heatexch_spec2', 'hybriddynamic_var', 'johnall', 'kan_peaks_h1_n2_g24', 'kan_peaks_h1_n2_g3', 'kan_peaks_h1_n5', 'kan_r3_h1_n3', 'kan_r3_h1_n9', 'kan_r5_h1_n3', 'kan_r5_h1_n5', 'kan_r5_h1_n8', 'kport20', 'kport40', 'lip', 'mbtd', 'multiplants_mtg1a', 'multiplants_mtg1b', 'multiplants_mtg1c', 'multiplants_mtg2', 'multiplants_mtg5', 'multiplants_mtg6', 'multiplants_stg1', 'multiplants_stg1a', 'multiplants_stg1b', 'multiplants_stg1c', 'multiplants_stg5', 'multiplants_stg6', 'nvs01', 'nvs05', 'nvs08', 'nvs21', 'nvs22', 'parallel', 'pooling_epa1', 'pooling_epa2', 'pooling_epa3', 'procsel', 'saa_2', 'sepasequ_complex', 'sepasequ_convent', 'sfacloc1_2_80', 'sfacloc1_2_90', 'sfacloc1_2_95', 'sfacloc1_3_80', 'sfacloc1_3_90', 'sfacloc1_3_95', 'sfacloc1_4_80', 'sfacloc1_4_90', 'sfacloc1_4_95', 'sfacloc2_2_80', 'sfacloc2_2_90', 'sfacloc2_2_95', 'sfacloc2_3_80', 'sfacloc2_3_90', 'sfacloc2_3_95', 'sfacloc2_4_80', 'sfacloc2_4_90', 'sfacloc2_4_95', 'spring', 'st_e15', 'st_e29', 'st_e32', 'st_e36', 'st_e38', 'supplychainp1_020306', 'supplychainp1_022020', 'supplychainp1_030510', 'supplychainr1_020306', 'supplychainr1_022020', 'supplychainr1_030510', 'synheat', 'tanksize', 'transswitch0014p', 'transswitch0030p', 'transswitch0039p', 'transswitch0118p', 'tspn05', 'tspn08', 'tspn10', 'tspn12', 'tspn15', 'unitcommit2', 'var_con10', 'var_con5', 'wastepaper3', 'wastepaper4', 'wastepaper5', 'wastepaper6', 'water4', 'waternd1', 'waternd2', 'waterno2_01', 'waterno2_02', 'waterno2_03', 'waterno2_04', 'waterno2_06', 'waterx', 'windfac']
if __name__ == "__main__":

    if len(argv) != 5:
        print("Usage: python create_plot.py <data_file.csv> <key> <solve_time> <analysis>")
        print("key: cvx or noncvx")
        print("solve_time: solvetime or totaltime")
        print("analysis: compare or alpha or rho or custom")
        exit(1)

    latexify(6, 4)
    data = pd.read_csv(argv[1])
    SAVE_DIRECTORY = os.path.dirname(argv[1])
    key = argv[2]
    assert (key == "cvx" or key == "noncvx")
    solve_time = argv[3]
    assert (solve_time == "solvetime" or solve_time == "totaltime")
    analysis = argv[4]
    assert (analysis == "compare" or analysis == "alpha" or analysis == "rho" or analysis=="custom")

    if analysis == "custom":
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

        solvers = [f"{key}_new", f"{key}_old",]
        solver_names = ["S-B-MIQP-new", "S-B-MIQP",]
        TAU_MAX = (1e2, 1e2)
        YLIM_LIST = [(0, 1), (0, 1)]

        # solvers = [f"{key}_sbmiqp_ee_new", f"{key}_sbmiqp_ee",]
        # solver_names = ["S-B-MIQP-ee-new", "S-B-MIQP-ee",]

    # =================== amplpy comparison ===================
    if analysis == "compare":
        solvers = [f"{key}_bonmin", f"{key}_gurobi", f"{key}_scip", f"{key}_shot", f"{key}_sbmiqp", f"{key}_sbmiqp_ee"]
        solver_names = ["Bonmin", "Gurobi", "SCIP", "SHOT", "S-B-MIQP", "S-B-MIQP-ee",]
        if key=='cvx':
            TAU_MAX = (1e5, 1e2)
            YLIM_LIST = [(0, 1), (0.5, 1)]
        else:
            TAU_MAX = (1e5, 1e5)
            YLIM_LIST = [(0, 1), (0, 1)]

    # =================== alpha comparison ===================
    if analysis == "alpha":
        solvers = [f"{key}_sbmiqp_ee_005", f"{key}_sbmiqp_ee_025", f"{key}_sbmiqp_ee_050", f"{key}_sbmiqp_ee_075", f"{key}_sbmiqp_ee_095",]
        solver_names = [r"$\alpha=0.05$", r"$\alpha=0.25$", r"$\alpha=0.50$", r"$\alpha=0.75$", r"$\alpha=0.95$"]
        TAU_MAX = (1e3, 1e2)
        YLIM_LIST = [(0, 1), (0.9, 1)]

    # =================== rho comparison ===================
    if analysis == "rho":
        solvers = [f"{key}_sbmiqp_010", f"{key}_sbmiqp_015", f"{key}_sbmiqp_050", f"{key}_sbmiqp_100", f"{key}_sbmiqp_500",]
        solver_names = [r"$\rho=1$", r"$\rho=1.5$", r"$\rho=5$", r"$\rho=10$", r"$\rho=50$"]
        data = data.loc[data["name"].isin(NONCVX_INSTANCES_WITH_CUT_CORRECTION)]
        TAU_MAX = (1.1e1, 1e2)
        YLIM_LIST = [(0, 1), (0.9, 1.005)]

    # ========================== END ==========================

    total_entries = data.shape[0]

    solvers_obj = [f"{solver}.obj" for solver in solvers]
    solvers_calctime = [solver + ".calc_time" for solver in solvers]
    if solve_time == "solvetime":
        for i in range(len(solvers_calctime)):
            if "sbmiqp" in solvers_calctime[i]:
                solvers_calctime[i] = solvers_calctime[i].split(".")[0] + ".solver_time"

    data[solvers_calctime] = data[solvers_calctime].map(to_float)
    data[solvers_obj] = data[solvers_obj].map(to_float)

    data['min.calctime'] = np.min(data[solvers_calctime], axis=1)
    data.set_index("name", inplace=True)

    for solver in solvers:
        if "shot" in solver:
            data.loc[data[f'{solver}.obj'] == np.inf, f'{solver}.calc_time'] = np.inf
        if "gurobi" in solver or "scip" in solver:
            mask = (data[f'{solver}.obj'].abs() > 1e10) | (data[f'{solver}.obj'] == 0)
            data.loc[mask, f'{solver}.calc_time'] = np.inf
            data.loc[mask, f'{solver}.obj'] = np.inf
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

    for s, ct, so in zip(solvers, solvers_calctime, solvers_obj):
        mask = data[ct] == 300
        gap  = rel_gap(data['primalbound'], data[f'{s}.obj'])
        failed = data[so] == np.inf
        print(f'{s}: \t\t success {total_entries-failed.sum()-mask.sum():3d} | fail {failed.sum():2d} | time-out {mask.sum():3d} , gap <1e-1 {(gap[mask]<1e-1).sum():2d}')

    # New plots:
    create_performance_profile(data, solvers_calctime, ylim=YLIM_LIST[0], tau_max=TAU_MAX[0], name=f'{key}_calc_time_profile_nsol{len(solver_names)}_{solve_time}', title="Wall time", legend_labels=solver_names, log_scale=True)
    create_performance_profile(data, solvers_obj, ylim=YLIM_LIST[1], tau_max=TAU_MAX[1], name=f'{key}_obj_profile_nsol{len(solver_names)}', title="Objective", legend_labels=solver_names, log_scale=True)

    plt.show()
