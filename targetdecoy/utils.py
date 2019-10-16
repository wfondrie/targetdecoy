"""
This module provides utility functions for the main functions of the
targetdecoy package
"""
import numpy as np
import pandas as pd
from itertools import izip, count

def fdr2qvalues(metric, fdr):
    """
    Calculates q-values from the estimated FDR.

    Parameters:
    -----------
    metric : numpy.array
        A 1D numpy array with the metric sorted from best to worst.

    fdr : numpy.array
        A 1D numpy array that is the corresponding FDR to the
        `metric`.

    Returns:
    --------
    numpy.array
        A 1D numpy array containing the calculated q-values in the
        same order as `metric`.
    """
    # Need to loop from worst to best
    metric = np.flip(metric).tolist()
    fdr = np.flip(fdr).tolist()

    # Gives the n-1 metric
    next_metric = metric[1:] + [None]

    min_q = 1
    group_fdr = 0
    num = 0
    qvals = []
    qvals_extend = qvals.extend
    for met, nxt, f in izip(metric, next_metric, fdr):
        if met == nxt:
            group_fdr = max([group_fdr, f])
            continue
        else:
            group_fdr = [f]
            

        if curr_fdr < min_q:
            min_q = curr_fdr

        qvals_extend([min_q] * num)

    qvals = np.array(qvals).flip()
    return qvals






