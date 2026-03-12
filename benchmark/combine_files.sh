# This file is part of camino-benchmark
# Copyright (C) 2025  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <mode> <path_to_output>"
    echo "Modes: compare, alpha, rho"
    exit 1
fi

path_to_output=$2
mode=$1
mkdir -p $path_to_output

case "$mode" in
    compare)
        echo "Running comparison mode..."
        # ============================== General Comparison ==============================
        python ./benchmark/to_csv.py $path_to_output/cvx_bonmin/overview.json $path_to_output/cvx_bonmin.csv
        python ./benchmark/to_csv.py $path_to_output/cvx_sbmiqp/overview.json $path_to_output/cvx_sbmiqp.csv
        python ./benchmark/to_csv.py $path_to_output/cvx_sbmiqp_ee/overview.json $path_to_output/cvx_sbmiqp_ee.csv
        python ./benchmark/to_csv.py $path_to_output/cvx_gurobi/overview.json $path_to_output/cvx_gurobi.csv
        python ./benchmark/to_csv.py $path_to_output/cvx_scip/overview.json $path_to_output/cvx_scip.csv

        python ./benchmark/to_csv.py $path_to_output/noncvx_bonmin/overview.json $path_to_output/noncvx_bonmin.csv
        python ./benchmark/to_csv.py $path_to_output/noncvx_sbmiqp/overview.json $path_to_output/noncvx_sbmiqp.csv
        python ./benchmark/to_csv.py $path_to_output/noncvx_sbmiqp_ee/overview.json $path_to_output/noncvx_sbmiqp_ee.csv
        python ./benchmark/to_csv.py $path_to_output/noncvx_gurobi/overview.json $path_to_output/noncvx_gurobi.csv
        python ./benchmark/to_csv.py $path_to_output/noncvx_scip/overview.json $path_to_output/noncvx_scip.csv

        python ./benchmark/read_shot.py ./benchmark/convex_set_full.csv $path_to_output/cvx_shot $path_to_output/cvx_shot.csv
        python ./benchmark/read_shot.py ./benchmark/nonconvex_set_full.csv $path_to_output/noncvx_shot $path_to_output/noncvx_shot.csv

        python ./benchmark/join_csv_using_pandas.py $path_to_output/cvx.csv ./benchmark/convex_set_full.csv $path_to_output/cvx_bonmin.csv $path_to_output/cvx_sbmiqp.csv $path_to_output/cvx_sbmiqp_ee.csv  $path_to_output/cvx_shot.csv $path_to_output/cvx_gurobi.csv $path_to_output/cvx_scip.csv
        python ./benchmark/join_csv_using_pandas.py $path_to_output/noncvx.csv ./benchmark/nonconvex_set_full.csv $path_to_output/noncvx_bonmin.csv $path_to_output/noncvx_sbmiqp.csv $path_to_output/noncvx_sbmiqp_ee.csv  $path_to_output/noncvx_shot.csv $path_to_output/noncvx_gurobi.csv $path_to_output/noncvx_scip.csv
        python ./benchmark/to_csv.py $path_to_output/cvx_sbmiqp/overview.json $path_to_output/cvx_sbmiqp.csv
        python ./benchmark/to_csv.py $path_to_output/cvx_sbmiqp_new/overview.json $path_to_output/cvx_sbmiqp_new.csv
        python ./benchmark/join_csv_using_pandas.py $path_to_output/cvx.csv ./benchmark/convex_set.csv $path_to_output/cvx_sbmiqp.csv $path_to_output/cvx_sbmiqp_new.csv $path_to_output/cvx_sbmiqp_ee.csv $path_to_output/cvx_sbmiqp_ee_new.csv
        python ./benchmark/join_csv_using_pandas.py $path_to_output/noncvx.csv ./benchmark/nonconvex_set.csv $path_to_output/noncvx_sbmiqp.csv $path_to_output/noncvx_sbmiqp_new.csv $path_to_output/noncvx_sbmiqp_ee.csv $path_to_output/noncvx_sbmiqp_ee_new.csv
        ;;
    alpha)
        # ============================== Combine files for comparing sbmiqp versions ==============================
        echo "Running alpha tuning mode..."
        # ============================== Combine files for tuning alpha in sbmiqp ==============================
        python ./benchmark/to_csv.py $path_to_output/overview005.json $path_to_output/cvx_sbmiqp_ee_005.csv
        python ./benchmark/to_csv.py $path_to_output/overview025.json $path_to_output/cvx_sbmiqp_ee_025.csv
        python ./benchmark/to_csv.py $path_to_output/overview050.json $path_to_output/cvx_sbmiqp_ee_050.csv
        python ./benchmark/to_csv.py $path_to_output/overview075.json $path_to_output/cvx_sbmiqp_ee_075.csv
        python ./benchmark/to_csv.py $path_to_output/overview095.json $path_to_output/cvx_sbmiqp_ee_095.csv
        python ./benchmark/join_csv_using_pandas.py $path_to_output/cvx.csv ./benchmark/convex_set_full.csv $path_to_output/cvx_sbmiqp_ee_005.csv $path_to_output/cvx_sbmiqp_ee_025.csv $path_to_output/cvx_sbmiqp_ee_050.csv $path_to_output/cvx_sbmiqp_ee_075.csv $path_to_output/cvx_sbmiqp_ee_095.csv
        ;;
    rho)
        echo "Running rho tuning mode..."
        # ============================== Combine files for tuning rho in sbmiqp ==============================
        python ./benchmark/to_csv.py $path_to_output/overview010.json  $path_to_output/noncvx_sbmiqp_010.csv
        python ./benchmark/to_csv.py $path_to_output/overview015.json  $path_to_output/noncvx_sbmiqp_015.csv
        python ./benchmark/to_csv.py $path_to_output/overview050.json  $path_to_output/noncvx_sbmiqp_050.csv
        python ./benchmark/to_csv.py $path_to_output/overview100.json  $path_to_output/noncvx_sbmiqp_100.csv
        python ./benchmark/to_csv.py $path_to_output/overview500.json  $path_to_output/noncvx_sbmiqp_500.csv
        python ./benchmark/join_csv_using_pandas.py $path_to_output/noncvx.csv ./benchmark/nonconvex_set_full.csv $path_to_output/noncvx_sbmiqp_010.csv $path_to_output/noncvx_sbmiqp_015.csv $path_to_output/noncvx_sbmiqp_050.csv $path_to_output/noncvx_sbmiqp_100.csv $path_to_output/noncvx_sbmiqp_500.csv
        ;;

    *)
        echo "Error: Mode '$mode' is not recognized."
        echo "Please use 'compare', 'alpha', or 'rho'."
        exit 1
        ;;
esac