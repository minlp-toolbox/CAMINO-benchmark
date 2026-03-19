path_to_file=$1
path_to_output=$2

mkdir -p $path_to_output

python benchmark/using_amplpy.py cvx gurobi $path_to_file $path_to_output
python benchmark/using_amplpy.py cvx scip $path_to_file $path_to_output
# python benchmark/using_amplpy.py cvx xpress $path_to_file $path_to_output

python benchmark/using_amplpy.py noncvx gurobi $path_to_file $path_to_output
python benchmark/using_amplpy.py noncvx scip $path_to_file $path_to_output
# python benchmark/using_amplpy.py noncvx xpress $path_to_file $path_to_output
