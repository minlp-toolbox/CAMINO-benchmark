import csv
from sys import argv
from math import isinf, nan

TIME_LIMIT = 300

file = argv[1]
key = argv[2]
assert (key == "cvx" or key == "noncvx")

solvers_keys = [f"{key}_bonmin", f"{key}_shot",
                f"{key}_sbmiqp", f"{key}_sbmiqp_ee",]
solvers_obj = [f"{solver}.obj" for solver in solvers_keys]
solvers_calctime = [
    solver + ".calc_time" if "shot" not in solver else f"{solver}.calctime"
    for solver in solvers_keys
]
solver_names = ["Bonmin", "SHOT", "S-B-MIQP", "S-B-MIQP-ee"]


print("Objective")
print("\\begin{center}")
print("\\begin{tabular}{l" + " r " * 5 + "} ")
print("\\toprule")
print(" & ".join(["Name", "Reference"] + solver_names) + " \\\\")
print("\\midrule")
with open(argv[1], newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        items = [row['name'].replace("_", "\\_"), "$%.3e$" % float(row['primalbound'])]
        for key, calc_key in zip(solvers_obj, solvers_calctime):
            try:
                calc_time = float(row[calc_key])
                value = float(row[key])
                if isinf(value):
                    value = nan

                if calc_time > TIME_LIMIT:
                    items.append("$%.3e$*" % value)
                else:
                    items.append("$%.3e$" % value)
            except Exception:
                if len(row[key]) > 20:
                    items.append("NAN")
                else:
                    items.append(row[key])

        print(" & ".join(items) + " \\\\")
print("\\bottomrule")
print("\\end{tabular}")
print("\\end{center}")

print("Time")
print("\\begin{center}")
print("\\begin{tabular}{l" + " r " * 4 + "} ")
print("\\toprule")
print(" & ".join(["Name"] + solver_names) + " \\\\")
print("\\midrule")
with open(argv[1], newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        items = [row['name'].replace("_", "\\_")]
        for key, calc_key in zip(solvers_obj, solvers_calctime):
            try:
                items.append("$%.3f$" % float(row[calc_key]))
            except Exception:
                if len(row[calc_key]) > 20:
                    items.append("NAN")
                else:
                    items.append(row[calc_key])
        print(" & ".join(items) + " \\\\")
print("\\bottomrule")
print("\\end{tabular}")
print("\\end{center}")
