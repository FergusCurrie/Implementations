"""
Run a task. This means 1 model with 1 set of parameters on 1 dataset. 
Args should be passed. jobid and taskid 
"""

from sklearn.model_selection import train_test_split
from experiments.get_experiment import get_experiment

import pandas as pd
import sys
import time
import os 


def select_task(taskid : int, experiment : dict):
    """
    Method for selecting current task out of all tasks in job.

    Args:
        taskid (int): Which task within experiment. A task is a combination of a model, a set of parameters and a dataset. 
        experiment (dict): Dictionary containing experiment data. 

    Returns:
        Model, str, dict: The model, dataset and parameters that define this task
    """
    i = 0
    for model in experiment["models"]:
        for param in model.params:
            for dataset_name in experiment["datasets"].keys():
                if i == int(taskid):
                    return model, dataset_name, param
                i += 1
    return None, None, None


# Unpack arguments


def run(jobid : int, taskid : int, name : str): 
    """
    Run a single task. 

    Careful. Grid can't handle a task id of 1. Therefore we refer to a task from 1, but is index from 0. 

    Args:
        jobid (int): Which job. A job is the number corresponding to the experiment (differnet grid runs of same exp have diff job ids). 
        taskid (int): Which task within experiment. A task is a combination of a model, a set of parameters and a dataset. 
    """
    # first make file system
    if not os.path.isdir(f'task_store/{jobid}'):
        os.mkdir(f'task_store/{jobid}')
    d = f'task_store/{jobid}/{taskid}/'
    os.mkdir(d)
    

    nseeds = 30
    results = []

    # Load Experiment
    print(f'Running {name}')
    experiment = get_experiment(name) # experiment is now a dict


    # Select correct task
    # Careful. Grid can't handle a task id of 1. Therefore we refer to a task from 1, but is index from 0. 
    model, dataset_name, param = select_task(taskid-1, experiment)
    dataset = experiment["datasets"][dataset_name]

    # Select the active parameter
    model.active_param = param

    # Split the data
    X = dataset[0]
    y = dataset[1]

    # Run for 30 seeds
    for i in range(nseeds):
        start = time.time()
        seed = 169 * i
        print(f'Run number {i}/{nseeds}  ... seed = {seed} of {dataset_name}')
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y) # NOTICE STRATIFICATION

        # Member generation 
        model.member_generation(X_train, y_train, seed)
        end = time.time()
        # Evaluation - post generation
        metrics = experiment["metrics"]
        training_results = model.ensemble_evaluation(X_train, y_train, metrics)
        test_results = model.ensemble_evaluation(X_test, y_test, metrics) # comes back as [[training, seed , tpr, ..]]
        results.append([True] + [True] + [seed] + [end - start] + training_results)
        results.append([True] + [False] + [seed] + [end - start] + test_results)
        # Save the models 
        #model.ensemble_save(jobid, taskid, seed, 'gen')

        # Member Selection
        start = time.time()
        model.member_selection(X_train, y_train)
        end = time.time()
        # Evaluation - post member selection 
        metrics = experiment["metrics"]
        training_results = model.ensemble_evaluation(X_train, y_train, metrics)
        test_results = model.ensemble_evaluation(X_test, y_test, metrics) # comes back as [[training, seed , tpr, ..]]
        results.append([False] + [True] + [seed] + [end - start] + training_results)
        results.append([False] + [False] + [seed] + [end - start] + test_results)
        #model.ensemble_save(jobid, taskid, seed, 'sel')

        # Save history
        #model.history.to_csv(f'task_store/history_{i}_{name}_job_{jobid}_task_{taskid}_{dataset_name}.csv')

    # Saving result - and History
    df = pd.DataFrame(data=results, columns = ['member_generation','training', 'seed', 'time', 'full_acc', 'majority_acc', 'minority_acc', 'tn', 'fp', 'fn', 'tp'])
    df.to_csv(f"{d}{name}_job_{jobid}_task_{taskid}_{dataset_name}.csv", index=False)


