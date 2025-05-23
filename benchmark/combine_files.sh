# This file is part of camino-benchmark
# Copyright (C) 2025  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later


path_to_output=$1
mkdir -p $1

python ./benchmark/to_csv.py $1/cvx_bonmin/overview.json $1/cvx_bonmin.csv
python ./benchmark/to_csv.py $1/cvx_sbmiqp/overview.json $1/cvx_sbmiqp.csv
python ./benchmark/to_csv.py $1/cvx_sbmiqp_ee/overview.json $1/cvx_sbmiqp_ee.csv
python ./benchmark/to_csv.py $1/noncvx_bonmin/overview.json $1/noncvx_bonmin.csv
python ./benchmark/to_csv.py $1/noncvx_sbmiqp/overview.json $1/noncvx_sbmiqp.csv
python ./benchmark/to_csv.py $1/noncvx_sbmiqp_ee/overview.json $1/noncvx_sbmiqp_ee.csv

python ./benchmark/read_shot.py ./benchmark/convex_set.csv $1/cvx_shot $1/cvx_shot.csv
python ./benchmark/read_shot.py ./benchmark/nonconvex_set.csv $1/noncvx_shot $1/noncvx_shot.csv

python ./benchmark/join_data.py $1/cvx.csv ./benchmark/convex_set.csv $1/cvx_bonmin.csv $1/cvx_sbmiqp.csv $1/cvx_sbmiqp_ee.csv $1/cvx_shot.csv
python ./benchmark/join_data.py $1/noncvx.csv ./benchmark/nonconvex_set.csv $1/noncvx_bonmin.csv $1/noncvx_sbmiqp.csv $1/noncvx_sbmiqp_ee.csv $1/noncvx_shot.csv
