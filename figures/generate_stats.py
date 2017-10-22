
import pandas as pd
import seaborn as sns
import numpy as np
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
import matplotlib as mpl
import scipy.stats
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import math
import argparse


pandas2ri.activate()
# import R's "base" package
base = importr('base')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'result_file',
        type=str,
        help='Pandas results'
    )

    args = parser.parse_args()


df = pd.read_pickle(args.result_file)

measures = ['SDR', 'ISR', 'SIR', 'SAR']


df = df.groupby(
        ['estimate_name', 'track_id', 'target_name']
).mean().reset_index()

# reshape data
df = pd.melt(
   df,
   id_vars=[
      'track_id',
      'target_name',
      'estimate_name',
      'is_supervised',
      'uses_augmentation'
   ],
   value_vars=measures,
   var_name='metric',
   value_name='score'
)
# make sure the subset is correct
df[['track_id']] = df[['track_id']].apply(pd.to_numeric)
df['subset'] = np.where(df['track_id'] >= 51, 'Dev', 'Test')
# import R's "utils" package
utils = importr('utils')
stats = importr('stats')

df_sdr_vocals_test = df.query(
   'metric == "SDR" and target_name == "vocals" and subset == "Test"'
)
df_sdr_vocals_dev = df.query(
   'metric == "SDR" and target_name == "vocals" and subset == "Dev"'
)

groups = np.unique(df_sdr_vocals_test["estimate_name"].values)
chi2_test, p_test = scipy.stats.friedmanchisquare(
   *[
      df_sdr_vocals_test[df_sdr_vocals_test["estimate_name"] == i]["score"]
      for i in groups
   ]
)

print("chi2 sdr vocals TEST: ", chi2_test)
print("p sdr vocals TEST: ", p_test)

chi2_dev, p_dev = scipy.stats.friedmanchisquare(
   *[
      df_sdr_vocals_dev[df_sdr_vocals_dev["estimate_name"] == i]["score"]
      for i in groups
   ]
)
print("chi2 sdr vocals DEV: ", chi2_dev)
print("p sdr vocals DEV: ", p_dev)

fit_test = stats.pairwise_wilcox_test(
    df_sdr_vocals_test['score'],
    df_sdr_vocals_test['estimate_name'],
    p_adjust_method="bonf",
    paired=True,
    exact=True
)

fit_dev = stats.pairwise_wilcox_test(
    df_sdr_vocals_dev['score'],
    df_sdr_vocals_dev['estimate_name'],
    p_adjust_method="bonf",
    paired=True,
    exact=True
)

pairwise_lower = np.array(fit_test[2])
pairwise_upper = np.array(fit_dev[2]).T

pairwise = np.zeros((pairwise_lower.shape[0] + 1, pairwise_lower.shape[1] + 1))
pairwise[np.tril_indices_from(pairwise, -1)] = pairwise_lower[
   np.tril_indices_from(pairwise_lower)
]
pairwise[np.triu_indices_from(pairwise, 1)] = pairwise_upper[
   np.triu_indices_from(pairwise_upper)
]

bounds = np.array([0, 0.05, 1])
mask = np.diag(np.ones(pairwise.shape[0]))
alphamap = colors.BoundaryNorm(boundaries=bounds, ncolors=256)

axis_labels = [fit_test[2].colnames[0]] + list(fit_test[2].rownames)

df_sort_by = df_sdr_vocals_test[
   (df_sdr_vocals_test.metric == 'SDR') & (df_sdr_vocals_test.subset == "Test")
]

sorted_estimates = df_sort_by.score.groupby(
   df_sort_by.estimate_name
).median().order().index.tolist()

sorted_indices = [axis_labels.index(label) for label in sorted_estimates]

pairwise = pairwise[sorted_indices, :]
pairwise = pairwise[:, sorted_indices]

plt.rc('text', usetex=True)
plt.rc('font', family='serif')

mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['text.latex.unicode'] = 'True'

# Get this from LaTeX using \showthe\columnwidth
fig_width_pt = 244.6937
# Convert pt to inch
inches_per_pt = 1.0 / 72.27
# Aesthetic ratio
golden_mean = (math.sqrt(5) - 1.0) / 2.0
# width in inches
fig_width = fig_width_pt * inches_per_pt
# height in inches
fig_height = fig_width * golden_mean
fig_size = np.array([fig_width*5, fig_height*4])

params = {
     'backend': 'ps',
     'axes.labelsize': 18,
     'font.size': 16,
     'legend.fontsize': 16,
     'xtick.labelsize': 15,
     'ytick.labelsize': 15,
     'text.usetex': True,
     'font.family': 'serif',
     'font.serif': 'ptmrr8re',
     'figure.figsize': fig_size
}

plt.rcParams.update(params)

sns.set_style("darkgrid", {
     "axes.facecolor": "0.925",
     'text.usetex': True,
     'font.family': 'serif',
     'axes.labelsize': 13,
     'font.size': 15,
     'legend.fontsize': 15,
     'xtick.labelsize': 15,
     'ytick.labelsize': 15,
     'font.serif': 'ptmrr8re',
})

f, ax = plt.subplots(1, 1, figsize=fig_size)

ax = sns.heatmap(
    np.flipud(pairwise),
    ax=ax,
    square=True,
    cbar=True,
    linewidths=.1,
    linecolor='lightgrey',
    mask=np.flipud(mask),
    norm=alphamap,
    cmap='OrRd',
    cbar_kws={
        'ticks': bounds,
        'label': 'p-value'
    },
    yticklabels=np.array(axis_labels)[sorted_indices[::-1]].tolist(),
    xticklabels=np.array(axis_labels)[sorted_indices].tolist()
)

ax.text(1, 22, 'Test', bbox={
   'edgecolor': "none",
   'facecolor': 'white',
   'alpha': 0.5,
   'pad': 5
},  fontsize=26)

ax.text(
   20, 2, 'Dev',
   bbox={'edgecolor': "none", 'facecolor': 'white', 'alpha': 0.5, 'pad': 5},
   fontsize=26
)

plt.setp(ax.get_yticklabels(), rotation=0)
plt.setp(ax.get_xticklabels(), rotation=90)

f.set_tight_layout(True)
f.savefig(
   "wilcox_voc_sdr.pdf",
   bbox_inches='tight',
   dpi=300
)
