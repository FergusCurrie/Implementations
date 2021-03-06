
from code.data_processing import get_data
from code.metrics.classification_metrics import *
from deap import gp
from deap import creator, base, tools
from deap.algorithms import varAnd
import numpy as np
import operator
import random
from code.metrics.classification_metrics import *
from code.learners.EC.deap_extra import GP_predict, get_pset
import pandas as pd 
from code.decision_fusion.voting import majority_voting


    

def get_toolbox(pset, t_size, max_depth, X, y, curr_ensemble):
    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=max_depth)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)
    toolbox.register("evaluate", bagging_fitness_calculation, toolbox=toolbox, X=X, y=y, ensemble=curr_ensemble) # HERE?
    toolbox.register("select", tools.selTournament, tournsize=t_size)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genHalfAndHalf, min_=0, max_=max_depth)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=max_depth))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=max_depth))
    return toolbox


def difference(pc1, pc2):
    dist = np.linalg.norm(pc1 - pc2)
    return dist 

def bagging_fitness_calculation(individual, toolbox, X, y, ensemble):
    """
    Fitness function. Compiles GP then tests
    """
    e1 = toolbox.compile(expr=individual)
    temp_ensemble = ensemble + [e1] 
    # check difference 
    delta = -np.inf
    for e2 in ensemble:
        d = difference(GP_predict(e1, X, np.unique(y)), GP_predict(e2, X, np.unique(y)))  # this uses the selection of the ensemble, think that is UCARP specific 
        if d > delta:
            delta = d
    if delta == 0:
        return -np.inf, 

    # calculate the temporary ensemble
    ypred = []
    for e in temp_ensemble:
        ypred.append(GP_predict(e, X, np.unique(y))) # might have to do one by one then combine
    ypred = np.array(ypred)
    ypred = majority_voting(ypred) # ypred should just be the length of the dataset
    #assert(ypred.shape == len(X))
    return accuracy(y, ypred), # here

def bagging_gp_member_generation(X,y, params, seed):
    random.seed(seed)
    # unpack parameters
    max_depth = params["max_depth"]
    pc = params["pc"]
    pm = params["pm"]
    ngen = params["ngen"]
    p_size = params['p_size']
    verbose = params["verbose"]
    t_size = params['t_size']
    curr_ensemble = params['ensemble']

    # Initalise primitives
    pset = get_pset(num_args=X.shape[1])

    # Initialise GP settings
    creator.create("FitnessMax", base.Fitness, weights=(1.0,)) # max
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    # Initalise tool box
    toolbox = get_toolbox(pset, t_size, max_depth, X, y, curr_ensemble)

    # Run GP
    pop = toolbox.population(n=p_size)

    halloffame = tools.HallOfFame(1)

    # Stats
    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("max", np.max)

    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (mstats.fields if mstats else [])
    df_data = []

    for gen in range(1, ngen + 1):
        #print(f'gen = {gen}')
        offspring_a = toolbox.select(pop, len(pop))
        offspring_a = varAnd(offspring_a, toolbox, pc, pm)
        invalid_ind = [ind for ind in offspring_a if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        if halloffame is not None:
            halloffame.update(offspring_a)
        pop[:] = offspring_a

        # Logging 
        record = mstats.compile(pop) 
        df_data.append(list(record['fitness'].values()) + list(record['size'].values()))

    # nodes, edges, labels = gp.graph(pop[0])


    return toolbox.compile(halloffame[0]), np.array(df_data), str(halloffame[0])
    #return [toolbox.compile(ind) for ind in pop], np.array(df_data), [str(ind) for ind in pop]


#######################################################################################################################
# Bagging 
#######################################################################################################################

def divbagging_member_generation(X, y, params, seed): # this is going to call the innergp a few times. 
    ncycles  = params['ncycles']
    batch_size = params['batch_size']
    ensemble = []
    ensemble_strings = []

    if batch_size == 'N':
        batch_size = len(y)
        params["batch_size"] = len(y)

    sum_history = np.ones((params['ngen'], 2))
    for c in range(ncycles):
        # evolve the ensemble for this cycle
        idx = np.random.choice(np.arange(len(X)), batch_size, replace=True)
        Xsubset = X[idx]
        ysubset = y[idx]
        params['ensemble'] = ensemble
        compiled_best, min_history, str_best = bagging_gp_member_generation(Xsubset, ysubset, params, seed+c)
        sum_history += min_history

        ensemble.append(compiled_best) # complied lambda
        ensemble_strings.append(str_best) # str of member 
    


    return ensemble, pd.DataFrame(data=(sum_history/ncycles)), ensemble_strings # temporarily only saving the first 

