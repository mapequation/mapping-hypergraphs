import numpy as np
import seaborn as sns


def plot_heatmap(data, **kwargs):
    return sns.heatmap(data,
                       vmax=1,
                       vmin=0.8,
                       mask=np.triu(np.ones_like(data, dtype=bool), k=1),
                       cmap=sns.color_palette("viridis", as_cmap=True),
                       annot=True,
                       annot_kws={"fontsize": 8},
                       fmt=".2g",
                       square=True,
                       linewidths=.5,
                       **kwargs)
