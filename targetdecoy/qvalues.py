"""
Function to estimate the FDR and q-values for a set of PSMs
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import methods

def estimate(metric, target, desc=True):
    """
    Estimate q-values using target decoy competition.

    Deprecated. See `methods.tdc()` instead
    """
    return methods.tdc(metric, target, desc)


def plot(qvalues, target=None, threshold=0.1, ax=None, **kwargs):
    """
    Plot the number of accepted PSMs at each q-value.

    Parameters
    ----------
    qvalues : numpy.ndarray
        The estimated q-values for a set of PSMs.

    target : numpy.ndarray, optional
        A 1D array indicating if the entry is from a target or decoy
        hit. This should be boolean, where `True` indicates a target
        and `False` indicates a decoy. `target[i]` is the label for
        `qvalues[i]`; thus `target` and `metric` should be of equal
        length. If `None` (the default), all elements of `qvalues` are
        assumed to be targets.

    threshold : float, optional
        Indicates the maximum q-value to plot, since often we are
        uninterested in performance at a high FDR. The default in 0.1.

    ax : matplotlib.pyplot.Axes, optional
        The matplotlib Axes on which to plot. If `None` the current Axes
        instance is used.

    **kwargs : dict
        Arguments passed to matplotlib.pyplot.plot()

    Returns
    -------
    matplotlib.pyplot.Axes
        A plot of the cumulative number of accepted targets.
    """
    # Change pd.Series to np.ndarray
    if isinstance(qvalues, pd.Series):
        qvalues = qvalues.values

    if isinstance(target, pd.Series):
        target = target.values
    elif target is None:
        target = np.ones(len(qvalues))

    # Check arguments
    msg = "'{}' must be a 1D numpy.ndarray or pandas.Series"
    if not isinstance(qvalues, np.ndarray):
        raise ValueError(msg.format("qvalues"))
    elif len(qvalues.shape) != 1:
        raise ValueError(msg.format("qvalues"))

    if not isinstance(target, np.ndarray):
        raise ValueError(msg.format("target"))
    elif len(target.shape) != 1:
        raise ValueError(msg.format("target"))

    if qvalues.shape[0] != target.shape[0]:
        raise ValueError("'qvalues' and 'target' must be the same length.")

    try:
        target = np.array(target, dtype=bool)
    except ValueError:
        raise ValueError("'target' should be boolean.")

    try:
        threshold = float(threshold)
    except ValueError:
        raise ValueError("'threshold' should be numeric.")

    if ax is None:
        ax = plt.gca()
    elif not isinstance(ax, plt.Axes):
        raise ValueError("'ax' must be a matplotlib Axes instance.")

    # Calculate cumulative targets at each q-value
    qvalues = pd.Series(qvalues, name="qvalues")
    target = pd.Series(target, name="target")
    dat = pd.concat([qvalues, target], axis=1)
    dat = dat.sort_values("qvalues", ascending=True)
    dat["num"] = dat["target"].cumsum()
    dat = dat.groupby(["qvalues"]).max().reset_index()
    dat = dat[["qvalues", "num"]]

    if True: #dat.qvalues[0]:
        zero = pd.DataFrame({"qvalues": dat.qvalues[0], "num": 0}, index=[-1])
        dat = pd.concat([zero, dat], sort=True).reset_index(drop=True)

    xmargin = threshold * 0.05
    ymax = dat.num[dat.qvalues <= (threshold + xmargin)].max()
    ymargin = ymax * 0.05
    #dat = dat.loc[dat.qvalues <= (threshold + xmargin)]

    # Set margins
    curr_ylims = ax.get_ylim()
    if curr_ylims[1] < ymax + ymargin:
        ax.set_ylim(0 - ymargin, ymax + ymargin)

    ax.set_xlim(0 - xmargin, threshold + xmargin)
    ax.set_xlabel("q-value")
    ax.set_ylabel("Accepted Target PSMs")

    return ax.step(dat.qvalues.values, dat.num.values, where="post", **kwargs)
