import pandas as pd
import argparse
import numpy as np
from bokeh.charts import BoxPlot, output_file, show
from bokeh.io import output_file, curdoc
from bokeh.layouts import row, column
from bokeh.models.widgets import Dropdown
from bokeh.models import ColumnDataSource, DataRange1d, Select

df = pd.read_pickle("out.pandas")

subsets = ['Dev', 'Test']
measures = ['SDR', 'ISR', 'SIR', 'SAR']
targets = ['vocals', 'accompaniment', 'drums', 'other']


# reshape data
df = pd.melt(
   df,
   id_vars=['track_id', 'track_name', 'target_name', 'estimate_name', 'is_supervised'],
   value_vars=measures,
   var_name='metric',
   value_name='score'
)

# fetch track_id
df[['track_id']] = df[['track_id']].apply(pd.to_numeric)
df['subset'] = np.where(df['track_id'] >= 51, 'Dev', 'Test')

subset = 'Dev'
measure = 'SDR'
target = 'vocals'

subset_select = Select(value=subset, title='Subset', options=subsets)
measure_select = Select(value=measure, title='Measure', options=measures)
target_select = Select(value=target, title='Target', options=targets)

df = df.dropna()
df_measure = df[
    (df.metric == measure) &
    (df.target_name == target) &
    (df.subset == subset)
]


def update_plot(attrname, old, new):
    subset = subset_select.value
    measure = measure_select.value
    target = target_select.value
    df_measure = df[
        (df.metric == measure) &
        (df.target_name == target) &
        (df.subset == subset)
    ]
    layout.children[0] = make_plot(df_measure)


def make_plot(df_measure):
    p = BoxPlot(
        df_measure,
        values='score',
        label='estimate_name',
        color='estimate_name',
        title="Comparison over all methods",
        outliers=False,
        plot_width=1024,
    )

    return p

plot = make_plot(df_measure)

subset_select.on_change('value', update_plot)
measure_select.on_change('value', update_plot)
target_select.on_change('value', update_plot)

controls = column(subset_select, measure_select, target_select)
layout = row(plot, controls)

curdoc().add_root(layout)
curdoc().title = "SISEC MUS 2016"
