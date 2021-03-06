"""
Experiment testing baselines. 
"""
import sys
from code.learners.EC.DivBaggingGP import divbagging_member_generation

from code.learners.EC.FastGPBag_RF import gp_rf_bagging_member_generation
sys.path.append("/")

from model import Model
from code.data_processing import get_all_datasets, get_data

from code.decision_fusion.voting import  majority_voting
from code.learners.EC.deap_extra import GP_predict
from code.metrics.classification_metrics import multi_class_metric
from sklearn.decomposition import PCA

def get_fast_dr_experiment():
    # name


    exp_name = "dr"
    # Datasets
    all_datasets = get_all_datasets()


    # Create the PCA dataset. 
    pca_datastes = {}
    for npcs in [1,2,3,4]:
        for d in all_datasets:
            X, y = get_data(d)
            pca = PCA(n_components=npcs)
            Xt = pca.fit_transform(X)
            pca_datastes[f'{d}_{npcs}'] = (Xt, y)

    # Metrics
    metrics = [multi_class_metric]

    # MODELS ###############################################################################################################
    # BaggingGP
    # BaggingGP
    # 500 20
    bag_params_1 = {"p_size": 500, "max_depth": 8, "pc": 0.6, "pm": 0.4, "ngen": 20, "verbose": False, "t_size": 7, 'ncycles':5, 'batch_size':'N'}
    bag_params = [bag_params_1]
    bag_model_pca = Model(
        member_generation_func=divbagging_member_generation,
        member_selection_func=None, # offEEl
        decision_fusion_func=majority_voting,
        params=bag_params,
        pred_func=GP_predict,
        model_name = f'pcabag'
    )

    models = [bag_model_pca]
    ########################################################################################################################





    # Calculat number of tasks
    n_tasks = 0
    for model in models:
        n_tasks += len(pca_datastes) * len(model.params)

    return {"datasets": pca_datastes, "metrics": metrics, "models": models, "n_tasks": n_tasks, "name": exp_name}


