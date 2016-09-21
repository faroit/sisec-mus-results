import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select
from bokeh.io import curdoc
from bokeh.models import Jitter
from bokeh.models import HoverTool

df = pd.read_pickle("out.pandas")

subsets = ['Dev', 'Test']
measures = ['SDR', 'ISR', 'SIR', 'SAR']
targets = ['vocals', 'accompaniment', 'drums', 'other']

# reshape data
df = pd.melt(
   df,
   id_vars=['track_id', 'target_name', 'estimate_name', 'is_supervised'],
   value_vars=measures,
   var_name='metric',
   value_name='score'
)

# fetch track_id
df[['track_id']] = df[['track_id']].apply(pd.to_numeric)
df['subset'] = np.where(df['track_id'] >= 51, 'Dev', 'Test')

estimate_names = sorted(df.estimate_name.unique().tolist())
track_ids = map(str, df.track_id.unique().tolist())

subset = 'Dev'
measure = 'SDR'
target = 'vocals'
track_id = '1'

subset_select = Select(value=subset, title='Subset', options=subsets)
measure_select = Select(value=measure, title='Measure', options=measures)
target_select = Select(value=target, title='Target', options=targets)
track_id_select = Select(value=track_id, title='Track ID', options=track_ids)

df = df.dropna()
df_measure = df[
    (df.metric == measure) &
    (df.target_name == target) &
    (df.subset == subset)
]

source = ColumnDataSource(
    data=dict(x=[], y=[], metric=[], target=[], subset=[], track_id=[])
)

hover = HoverTool(tooltips=[
    ("Track ID", "@track_id"),
    ("Score", "@y"),
])

p = figure(
    plot_height=400,
    plot_width=1024,
    title="Fu",
    tools=[hover, "pan,wheel_zoom,box_select,lasso_select,reset"],
    x_range=estimate_names
)
p.circle(
    x="x",
    y="y",
    source=source,
    size=7,
    color="orange",
    fill_alpha=.5,
    line_width=0.1,
    line_color="orange"
)


controls = [subset_select, measure_select, target_select]


def update():
    subset = subset_select.value
    measure = measure_select.value
    target = target_select.value
    df_measure = df[
        (df.metric == measure) &
        (df.target_name == target) &
        (df.subset == subset)
    ]
    d = ColumnDataSource(data=df_measure)

    # df_measure.fillna(0, inplace=True)
    p.xaxis.axis_label = "Estimate"
    p.yaxis.axis_label = measure_select.value
    p.title.text = subset
    p.y_range.start = min(d.data['score']) - 3
    p.y_range.end = max(d.data['score']) + 3

    source.data = dict(
        x=d.data['estimate_name'],
        y=d.data['score'],
        metric=d.data["metric"],
        target=d.data["target_name"],
        subset=d.data["subset"],
        track_id=d.data["track_id"]
    )

update()

for control in controls:
    control.on_change('value', lambda attr, old, new: update())

layout = row(p, column(*controls))

curdoc().add_root(layout)
curdoc().title = "SISEC MUS 2016"
