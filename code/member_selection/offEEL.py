"""
From an ensemble selec
From this paper : https://dl.acm.org/doi/10.1145/1276958.1277317

"""
from code.metrics.classification_metrics import *
from typing import Callable


def offEEL(ensemble : list, X : np.array, y : np.array, decision_fusion_func : Callable, params) -> list:
    #print('start offeel')
    # First sort population 
    sorted_ensemble = sorted(ensemble, key=lambda member : accuracy(y, member.predict(X, np.unique(y))), reverse=True) # DESCENDING 
    #print(len(sorted_ensemble))
    # Now loop through an 
    best = [-1, -1] # ind, acc
    for i in range(len(sorted_ensemble)-1):
        F = sorted_ensemble[0:i+1]
        
        raw_ypred = np.array([learner.predict(X, np.unique(y)) for learner in F])

        # Then calculate true predictions with decision function
        ypred = decision_fusion_func(raw_ypred)

        acc = accuracy(y, ypred)
        if best[1] < acc:
            best = [i, acc]


    return sorted_ensemble[0:best[0]+1]