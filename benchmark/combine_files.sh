# This file is part of camino-benchmark
# Copyright (C) 2025  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later


path_to_output=$1
mkdir -p $1

python ./benchmark/to_csv.py $1/cvx_bonmin/overview.json $1/cvx_bonmin.csv
python ./benchmark/to_csv.py $1/cvx_sbmiqp/overview.json $1/cvx_sbmiqp.csv
# python ./benchmark/to_csv.py $1/cvx_gurobi/overview.json $1/cvx_gurobi.csv
# python ./benchmark/to_csv.py $1/cvx_scip/overview.json $1/cvx_scip.csv
python ./benchmark/to_csv.py $1/cvx_sbmiqp_ee/overview.json $1/cvx_sbmiqp_ee.csv
python ./benchmark/to_csv.py $1/noncvx_bonmin/overview.json $1/noncvx_bonmin.csv
python ./benchmark/to_csv.py $1/noncvx_sbmiqp/overview.json $1/noncvx_sbmiqp.csv
python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee/overview.json $1/noncvx_sbmiqp_ee.csv

python ./benchmark/read_shot.py ./benchmark/convex_set.csv $1/cvx_shot $1/cvx_shot.csv
python ./benchmark/read_shot.py ./benchmark/nonconvex_set.csv $1/noncvx_shot $1/noncvx_shot.csv

python ./benchmark/join_data.py $1/cvx.csv ./benchmark/convex_set.csv $1/cvx_bonmin.csv $1/cvx_sbmiqp.csv $1/cvx_sbmiqp_ee.csv  $1/cvx_shot.csv # $1/cvx_gurobi.csv $1/cvx_scip.csv
python ./benchmark/join_data.py $1/noncvx.csv ./benchmark/nonconvex_set.csv $1/noncvx_bonmin.csv $1/noncvx_sbmiqp.csv $1/noncvx_sbmiqp_ee.csv $1/noncvx_shot.csv


# ============================== Combine files for tuning alpha in sbmiqp ==============================
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_005/overview.json $1/cvx_sbmiqp_005.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_025/overview.json $1/cvx_sbmiqp_025.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_050/overview.json $1/cvx_sbmiqp_050.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_075/overview.json $1/cvx_sbmiqp_075.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_095/overview.json $1/cvx_sbmiqp_095.csv
# python ./benchmark/join_data.py $1/cvx.csv ./benchmark/convex_set.csv $1/cvx_sbmiqp_005.csv $1/cvx_sbmiqp_025.csv $1/cvx_sbmiqp_050.csv $1/cvx_sbmiqp_075.csv $1/cvx_sbmiqp_095.csv


# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_005/overview.json $1/noncvx_sbmiqp_005.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_025/overview.json $1/noncvx_sbmiqp_025.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_050/overview.json $1/noncvx_sbmiqp_050.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_075/overview.json $1/noncvx_sbmiqp_075.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_095/overview.json $1/noncvx_sbmiqp_095.csv
# python ./benchmark/join_data.py $1/noncvx.csv ./benchmark/nonconvex_set.csv $1/noncvx_sbmiqp_005.csv $1/noncvx_sbmiqp_025.csv $1/noncvx_sbmiqp_050.csv $1/noncvx_sbmiqp_075.csv $1/noncvx_sbmiqp_095.csv


# python ./benchmark/to_csv.py $1/cvx_sbmiqp_ee_005/overview.json $1/cvx_sbmiqp_ee_005.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_ee_025/overview.json $1/cvx_sbmiqp_ee_025.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_ee_050/overview.json $1/cvx_sbmiqp_ee_050.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_ee_075/overview.json $1/cvx_sbmiqp_ee_075.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_ee_095/overview.json $1/cvx_sbmiqp_ee_095.csv
# python ./benchmark/join_data.py $1/cvx_ee.csv ./benchmark/convex_set.csv $1/cvx_sbmiqp_ee_005.csv $1/cvx_sbmiqp_ee_025.csv $1/cvx_sbmiqp_ee_050.csv $1/cvx_sbmiqp_ee_075.csv $1/cvx_sbmiqp_ee_095.csv

# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_005/overview.json $1/noncvx_sbmiqp_ee_005.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_025/overview.json $1/noncvx_sbmiqp_ee_025.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_050/overview.json $1/noncvx_sbmiqp_ee_050.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_075/overview.json $1/noncvx_sbmiqp_ee_075.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_095/overview.json $1/noncvx_sbmiqp_ee_095.csv
# python ./benchmark/join_data.py $1/noncvx_ee.csv ./benchmark/nonconvex_set.csv $1/noncvx_sbmiqp_ee_005.csv $1/noncvx_sbmiqp_ee_025.csv $1/noncvx_sbmiqp_ee_050.csv $1/noncvx_sbmiqp_ee_075.csv $1/noncvx_sbmiqp_ee_095.csv


# ============================== Combine files for tuning rho in sbmiqp ==============================
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_rho_1.0/overview.json $1/noncvx_sbmiqp_rho_1.0.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_rho_1_5/overview.json $1/noncvx_sbmiqp_rho_1_5.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_rho_5.0/overview.json $1/noncvx_sbmiqp_rho_5.0.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_rho_10.0/overview.json $1/noncvx_sbmiqp_rho_10.0.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_rho_50.0/overview.json $1/noncvx_sbmiqp_rho_50.0.csv
# python ./benchmark/join_data.py $1/noncvx.csv ./benchmark/nonconvex_set.csv $1/noncvx_sbmiqp_rho_1.0.csv $1/noncvx_sbmiqp_rho_1_5.csv $1/noncvx_sbmiqp_rho_5.0.csv $1/noncvx_sbmiqp_rho_10.0.csv $1/noncvx_sbmiqp_rho_50.0.csv

# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_rho_1.0/overview.json $1/noncvx_sbmiqp_ee_rho_1.0.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_rho_1_5/overview.json $1/noncvx_sbmiqp_ee_rho_1_5.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_rho_5.0/overview.json $1/noncvx_sbmiqp_ee_rho_5.0.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_rho_10.0/overview.json $1/noncvx_sbmiqp_ee_rho_10.0.csv
# python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee_rho_50.0/overview.json $1/noncvx_sbmiqp_ee_rho_50.0.csv
# python ./benchmark/join_data.py $1/noncvx_ee.csv ./benchmark/nonconvex_set.csv $1/noncvx_sbmiqp_ee_rho_1.0.csv $1/noncvx_sbmiqp_ee_rho_1_5.csv $1/noncvx_sbmiqp_ee_rho_5.0.csv $1/noncvx_sbmiqp_ee_rho_10.0.csv $1/noncvx_sbmiqp_ee_rho_50.0.csv
