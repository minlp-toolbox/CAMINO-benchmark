# This file is part of camino-benchmark
# Copyright (C) 2026  Andrea Ghezzi, Wim Van Roy, Sebastian Sager, Moritz Diehl
# SPDX-License-Identifier: GPL-3.0-or-later


import json
import os
from sys import argv

RESULT_DIR = os.path.dirname(argv[1])
key = argv[2]
assert (key == "cvx" or key == "noncvx")

with open(argv[1], 'r') as file:
    data = json.load(file)
    data = data['data']

dimension_success_problem = len(data[0])
problems_with_cut_correction = []
for d in data[1:]:
    if len(d) != dimension_success_problem:
        pass
    else:
        if d[-1]:
            problems_with_cut_correction.append(d[1].split("/")[-1])

print(problems_with_cut_correction)
