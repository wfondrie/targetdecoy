"""
Test that the q-values estimated by the qvalues module are correct
"""
import pytest
import numpy as np
from targetdecoy import qvalues

SCORES1 = np.array([10, 10, 9, 8, 7, 7, 6, 5, 4, 3, 2, 2,  1,  1,  1,  1])
SCORES2 = np.array([ 1,  1, 2, 3, 4, 4, 5, 6, 7, 8, 9, 9, 10, 10, 10, 10])
TARGET  = np.array([ 1,  1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0,  0,  0,  0,  0])
QVALUES = np.array([ 1/4, 1/4, 1/4, 1/4, 2/6, 2/6, 2/6,
                     3/7, 3/7, 4/7, 5/8, 5/8, 1, 1, 1, 1])

def test_descending_scores():
    qvals = qvalues.estimate(SCORES1, TARGET, desc=True).tolist()
    assert qvals == QVALUES.tolist()

def test_ascending_scores():
    qvals = qvalues.estimate(SCORES2, TARGET, desc=False).tolist()
    assert qvals == QVALUES.tolist()

