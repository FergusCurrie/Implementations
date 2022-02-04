import numpy as np


def binary_voting(ypred : np.array) -> np.array:
    """
    Take a 2D np array of (n_learners, n_datapoints) and average along learn axis.
    Threshold to 0/1 depending on if value is closer

    Args:
        ypred (np.array): 2d array of predictions

    Returns:
        np.array: 1d array of predictions with shape (n_datapoints)
    """
    avg = np.sum(ypred, axis=0) / ypred.shape[0]
    avg[avg >= 0.5] = 1
    avg[avg < 0.5] = 0
    return avg