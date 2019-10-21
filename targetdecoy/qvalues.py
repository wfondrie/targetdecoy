"""
Function to estimate the FDR and q-values for a set of PSMs
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def estimate(metric, target, desc=True):
    """
    Estimate q-values using target decoy competition.

    Estimates q-values using the simple target decoy competition method.
    For set of target and decoy PSMs meeting a specified score threshold,
    the false discovery rate (FDR) is estimated as:

    ...math:
        FDR = \frac{Decoys + 1}{Targets}

    More formally, let the scores of target and decoy PSMs be indicated as
    :math:`f_1, f_2, ..., f_{m_f}` and :math:`d_1, d_2, ..., d_{m_d}`,
    respectively. For a score threshold :math:`t`, the false discovery
    rate is estimated as:

    ...math:
        E\{FDR(t)\} = \frac{|\{d_i > t; i=1, ..., m_d\}| + 1}
        {\{|f_i > t; i=1, ..., m_f|\}}

    The reported q-value for each PSM is the minimum FDR at which that
    PSM would be accepted.

    Parameters
    ----------
    metric : numpy.ndarray
        A 1D array containing the score to rank by (`float`)

    target : numpy.ndarray
        A 1D array indicating if the entry is from a target or decoy
        hit. This should be boolean, where `True` indicates a target
        and `False` indicates a decoy. `target[i]` is the label for
        `metric[i]`; thus `target` and `metric` should be of
        equal length.

    desc : bool
        Are higher scores better? `True` indicates that they are,
        `False` indicates that they are not.

    Returns
    -------
    numpy.ndarray
        A 1D array with the estimated q-value for each entry. The
        array is the same length as the `metric` and `target` arrays.
    """
    # Change pd.Series to np.ndarray
    if isinstance(metric, pd.Series):
        metric = metric.values

    if isinstance(target, pd.Series):
        target = target.values

    # Check arguments
    msg = "'{}' must be a 1D numpy.ndarray or pandas.Series"
    if not isinstance(metric, np.ndarray):
        raise ValueError(msg.format("metric"))
    elif len(metric.shape) != 1:
        raise ValueError(msg.format("metric"))

    if not isinstance(target, np.ndarray):
        raise ValueError(msg.format("target"))
    elif len(target.shape) != 1:
        raise ValueError(msg.format("target"))

    if not isinstance(desc, bool):
        raise ValueError("'desc' must be boolean (True or False)")

    if metric.shape[0] != target.shape[0]:
        raise ValueError("'metric' and 'target' must be the same length")

    try:
        target = np.array(target, dtype=bool)
    except ValueError:
        raise ValueError("'target' should be boolean.")

    # Sort and estimate FDR
    if desc:
        srt_idx = np.argsort(-metric)
    else:
        srt_idx = np.argsort(metric)

    metric = metric[srt_idx]
    target = target[srt_idx]
    cum_targets = target.cumsum()
    cum_decoys = ((target-1)**2).cumsum()
    num_total = cum_targets + cum_decoys

    fdr = (cum_decoys + 1) / cum_targets

    # Calculate q-values
    unique_metric, indices = np.unique(metric, return_counts=True)

    # Some arrays need to be flipped so that we can loop through from
    # worse to best score.
    fdr = np.flip(fdr)
    num_total = np.flip(num_total)
    if not desc:
        unique_metric = np.flip(unique_metric)
        indices = np.flip(indices)

    min_q = 1
    qvals = np.ones(len(fdr))
    group_fdr = np.ones(len(fdr))
    prev_idx = 0
    for idx in range(unique_metric.shape[0]):
        next_idx = prev_idx + indices[idx]
        group = slice(prev_idx, next_idx)
        prev_idx = next_idx
        fdr_group = fdr[group]
        n_group = num_total[group]
        n_max = n_group.max()
        curr_fdr = fdr_group[n_group == n_max]
        if curr_fdr[0] < min_q:
            min_q = curr_fdr[0]

        group_fdr[group] = curr_fdr
        qvals[group] = min_q

    # Restore the original order
    qvals = np.flip(qvals)
    qvals = qvals[np.argsort(srt_idx)]

    return qvals


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

    zero = pd.DataFrame({"qvalues": 0, "num": 0}, index=[-1])
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

    return ax.step(dat.qvalues.values, dat.num.values, **kwargs)
