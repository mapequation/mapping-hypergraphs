from typing import Optional

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


def plot_heatmap(data: pd.DataFrame, title: Optional[str] = None, **kwargs) -> plt.Figure:
    plt.figure()

    plot = sns.heatmap(data,
                       mask=np.triu(np.ones_like(data, dtype=bool), k=1),
                       yticklabels=data.columns,
                       cmap=(sns.color_palette("viridis", as_cmap=True)),
                       annot=True,
                       annot_kws={"fontsize": 8},
                       fmt=".2g",
                       square=True,
                       linewidths=.5,
                       **kwargs)

    if title:
        plt.title(title)
    plt.subplots_adjust(bottom=0.28)
    plt.show()

    return plot.get_figure()
