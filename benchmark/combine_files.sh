# This file is part of camino-benchmark
# Copyright (C) 2025  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later


path_to_output=$1
mkdir -p $1

python ./benchmark/to_csv.py $1/cvx_bonmin/overview.json $1/cvx_bonmin.csv
python ./benchmark/to_csv.py $1/cvx_sbmiqp/overview.json $1/cvx_sbmiqp.csv
python ./benchmark/to_csv.py $1/cvx_sbmiqp_ee/overview.json $1/cvx_sbmiqp_ee.csv
python ./benchmark/to_csv.py $1/cvx_gurobi/overview.json $1/cvx_gurobi.csv
python ./benchmark/to_csv.py $1/cvx_scip/overview.json $1/cvx_scip.csv

python ./benchmark/to_csv.py $1/noncvx_bonmin/overview.json $1/noncvx_bonmin.csv
python ./benchmark/to_csv.py $1/noncvx_sbmiqp/overview.json $1/noncvx_sbmiqp.csv
python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee/overview.json $1/noncvx_sbmiqp_ee.csv
python ./benchmark/to_csv.py $1/noncvx_gurobi/overview.json $1/noncvx_gurobi.csv
python ./benchmark/to_csv.py $1/noncvx_scip/overview.json $1/noncvx_scip.csv

python ./benchmark/read_shot.py ./benchmark/convex_set_full.csv $1/cvx_shot $1/cvx_shot.csv
python ./benchmark/read_shot.py ./benchmark/nonconvex_set_full.csv $1/noncvx_shot $1/noncvx_shot.csv

python ./benchmark/join_data.py $1/cvx.csv ./benchmark/convex_set_full.csv $1/cvx_bonmin.csv $1/cvx_sbmiqp.csv $1/cvx_sbmiqp_ee.csv  $1/cvx_shot.csv $1/cvx_gurobi.csv $1/cvx_scip.csv
python ./benchmark/join_data.py $1/noncvx.csv ./benchmark/nonconvex_set_full.csv $1/noncvx_bonmin.csv $1/noncvx_sbmiqp.csv $1/noncvx_sbmiqp_ee.csv  $1/noncvx_shot.csv $1/noncvx_gurobi.csv $1/noncvx_scip.csv

# ============================== Combine files for comparing sbmiqp versions ==============================
# python ./benchmark/to_csv.py $1/cvx_sbmiqp/overview.json $1/cvx_sbmiqp.csv
# python ./benchmark/to_csv.py $1/cvx_sbmiqp_new/overview.json $1/cvx_sbmiqp_new.csv
# python ./benchmark/join_data.py $1/cvx.csv ./benchmark/convex_set.csv $1/cvx_sbmiqp.csv $1/cvx_sbmiqp_new.csv $1/cvx_sbmiqp_ee.csv $1/cvx_sbmiqp_ee_new.csv
# python ./benchmark/join_data.py $1/noncvx.csv ./benchmark/nonconvex_set.csv $1/noncvx_sbmiqp.csv $1/noncvx_sbmiqp_new.csv $1/noncvx_sbmiqp_ee.csv $1/noncvx_sbmiqp_ee_new.csv


# ============================== Combine files for tuning alpha in sbmiqp ==============================
# python ./benchmark/to_csv.py $1/overview005.json $1/cvx_sbmiqp_ee_005.csv
# python ./benchmark/to_csv.py $1/overview025.json $1/cvx_sbmiqp_ee_025.csv
# python ./benchmark/to_csv.py $1/overview050.json $1/cvx_sbmiqp_ee_050.csv
# python ./benchmark/to_csv.py $1/overview075.json $1/cvx_sbmiqp_ee_075.csv
# python ./benchmark/to_csv.py $1/overview095.json $1/cvx_sbmiqp_ee_095.csv
# python ./benchmark/join_data.py $1/cvx.csv ./benchmark/convex_set_full.csv $1/cvx_sbmiqp_ee_005.csv $1/cvx_sbmiqp_ee_025.csv $1/cvx_sbmiqp_ee_050.csv $1/cvx_sbmiqp_ee_075.csv $1/cvx_sbmiqp_ee_095.csv


# ============================== Combine files for tuning rho in sbmiqp ==============================
# python ./benchmark/to_csv.py $1/overview_010.json  $1/noncvx_sbmiqp_010.csv
# python ./benchmark/to_csv.py $1/overview_015.json  $1/noncvx_sbmiqp_015.csv
# python ./benchmark/to_csv.py $1/overview_050.json  $1/noncvx_sbmiqp_050.csv
# python ./benchmark/to_csv.py $1/overview_100.json  $1/noncvx_sbmiqp_100.csv
# python ./benchmark/to_csv.py $1/overview_500.json  $1/noncvx_sbmiqp_500.csv
# python ./benchmark/join_data.py $1/noncvx.csv ./benchmark/nonconvex_set_full.csv $1/noncvx_sbmiqp_010.csv $1/noncvx_sbmiqp_015.csv $1/noncvx_sbmiqp_050.csv $1/noncvx_sbmiqp_100.csv $1/noncvx_sbmiqp_500.csv
