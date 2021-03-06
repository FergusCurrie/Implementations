# Code for MOGP 
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

def get_toolbox(pset, t_size, max_depth, X, y):
    toolbox = base.Toolbox()
    toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=max_depth)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("compile", gp.compile, pset=pset)
    toolbox.register("evaluate", fitness_calculation, toolbox=toolbox, X=X, y=y) # HERE?
    toolbox.register("select", tools.selTournament, tournsize=t_size)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", gp.genHalfAndHalf, min_=0, max_=max_depth)
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=max_depth))
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=max_depth))
    return toolbox

def fitness_calculation(individual, toolbox, X, y, w=0.5):
    """
    Fitness function. Compiles GP then tests
    """
    func = toolbox.compile(expr=individual)
    # Calculated the 'ave' function
    ypred = GP_predict(func, X, np.unique(y))
    acc = accuracy(y, ypred) # this is 
    return acc,

def gp_member_generation(X,y, params, seed):
    random.seed(seed)
    # default fitness function
    fitness_func = fitness_calculation
    # unpack parameters
    max_depth = params["max_depth"]
    pc = params["pc"]
    pm = params["pm"]
    ngen = params["ngen"]
    p_size = params['p_size']
    verbose = params["verbose"]
    t_size = params['t_size']

    if 'bagging' in params:
        fitness_func = params['fitness_function']
        curr_ensemble = params['current_ensemble']

    # Initalise primitives
    pset = get_pset(num_args=X.shape[1])

    # Initialise GP settings
    creator.create("FitnessMax", base.Fitness, weights=(1.0,)) # max
    creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

    # Initalise tool box
    toolbox = get_toolbox(pset, t_size, max_depth, X, y)

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

    # Evolution process 
    for gen in range(1, ngen + 1):
        
        #if verbose:
            #print(f'Generation {gen}/{ngen}')
        
        

        # Select the next generation individuals
        offspring_a = toolbox.select(pop, len(pop))

        # Vary the pool of individuals
        offspring_a = varAnd(offspring_a, toolbox, pc, pm)

        # Update pop a
        invalid_ind = [ind for ind in offspring_a if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring_a)


        # Replace the current population by the offspring
        pop[:] = offspring_a

        # Append the current generation statistics to the logbook
        record = mstats.compile(pop) if mstats else {}
        logbook.record(gen=gen, nevals=len(invalid_ind), **record)
        if verbose:
            print(logbook.stream)

    df = pd.DataFrame(logbook)
    return [toolbox.compile(ind) for ind in pop], df, [str(ind) for ind in pop]


