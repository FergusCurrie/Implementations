from run_a_task import run
import sys
from experiments.get_experiment import get_experiment

name = 'm3gp_bag'#"divmogp_experiment"#"fastbag"
experiment = get_experiment(name)

jobid = int(sys.argv[1])
taskid = int(sys.argv[2])
run(jobid, taskid, experiment['name'])