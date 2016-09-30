import pandas as pd
import numpy as np
from bokeh.plotting import figure
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Select
from bokeh.io import curdoc
from bokeh.models import Jitter, LinearColorMapper, Range1d
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
track_ids = map(int, df.track_id.unique().tolist())

subset = 'Dev'
measure = 'SDR'
target = 'vocals'
track_id = '1'

subset_select = Select(value=subset, title='Subset', options=subsets)
measure_select = Select(value=measure, title='Measure', options=measures)
target_select = Select(value=target, title='Target', options=targets)
# track_id_select = Select(value=track_id, title='Track ID', options=track_ids)

df = df.dropna()
df.to_json("out.json")
df_measure = df[
    (df.metric == measure) &
    (df.target_name == target) &
    (df.subset == subset)
]

source = ColumnDataSource(
    data=dict(x=[], y=[], metric=[], target=[], subset=[], score=[])
)

hover = HoverTool(tooltips=[
    ("Track ID", "@y"),
    ("Score", "@score"),
])

p = figure(
    plot_height=800,
    plot_width=1400,
    title="Fu",
    tools=[hover, "pan,wheel_zoom,box_select,lasso_select,reset"],
    x_range=estimate_names,
    y_range=Range1d(51, 100)
)

p2 = figure(
    plot_height=400,
    plot_width=1400,
    title="Score over methods",
    tools=["pan,wheel_zoom,box_select,lasso_select,reset"],
    x_range=estimate_names,
)

colors = [
    "#75968f",
    "#a5bab7",
    "#c9d9d3",
    "#e2e2e2",
    "#dfccce",
    "#ddb7b1",
    "#cc7878",
    "#933b41",
    "#550b1d"
]

mapper = LinearColorMapper(palette=colors)

p2.circle(
    x="x",
    y="score",
    source=source,
    line_color=None,
)

p.rect(
    x="x",
    y="y",
    width=1,
    height=1,
    source=source,
    line_color=None,
    fill_color={'field': 'score', 'transform': mapper},
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
    if subset == 'Dev':
        p.y_range.start = 51.5
        p.y_range.end = 100.5
    else:
        p.y_range.start = 0.5
        p.y_range.end = 50.5

    source.data = dict(
        y=map(int, d.data['track_id']),
        x=d.data['estimate_name'],
        metric=d.data["metric"],
        target=d.data["target_name"],
        subset=d.data["subset"],
        score=d.data["score"]
    )


update()

for control in controls:
    control.on_change('value', lambda attr, old, new: update())

layout = row(column(p2, p), column(*controls))

curdoc().add_root(layout)
curdoc().title = "SISEC MUS 2016"
