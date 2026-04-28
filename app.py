import pandas as pd
import panel as pn
import plotly.graph_objs as go
import locale

from data import get_data
from components.summary import create_summary_row
from components.sidebar import create_sidebar

pn.extension('perspective', 'echarts')

df = get_data()

# print(df.groupby(df["Activity Date"].dt.weekday)["Distance"].sum().reset_index().rename(columns={"Activity Date": "Month", "Distance": "Total Distance (km)"}))

dff = df[["Activity Date", "Activity Name", "Sport", "Elapsed Time"]].groupby("Sport")["Elapsed Time"].sum()


metric_selector = pn.widgets.RadioButtonGroup(
    name="Métrique",
    options=["Distance", "Elapsed time", "Total Elevation gain", "Nombre d'activité"],
    value="Distance",
    button_style="outline",
    button_type="primary",
)

interval_selector = pn.widgets.RadioButtonGroup(
    name="Intervalle",
    options=["Jours", "Semaines", "Mois", "Années"],
    value="Mois",
    button_style="outline",
    button_type="primary",
)

row1 = pn.Row(
    pn.pane.Plotly(
        df.groupby(pd.Grouper(key="Activity Date", freq="ME"))["Distance"]
            .sum()
            .reset_index()
            .pipe(
            lambda d: {
                "data": [
                    {
                        "x": d["Activity Date"],
                        "y": d["Distance"],
                        "type": "bar",
                    }
                ],
                "layout": {
                    "title": "Total Distance per Month",
                    "xaxis": {"title": "Month"},
                    "yaxis": {"title": "Total Distance (km)"},
                },
            }
        ),
        sizing_mode="stretch_width",
    ),
    pn.pane.Plotly(
        df.groupby([pd.Grouper(key="Activity Date", freq="W-MON"), "Sport"])["Distance"]
            .sum()
            .reset_index()
            .pivot(index="Activity Date", columns="Sport", values="Distance")
            .fillna(0)
            .pipe(
                lambda pivot: {
                    "data": [
                        {
                            # shift week labels one week earlier so each bar represents the week starting a week before
                            "x": (pivot.index - pd.Timedelta(weeks=1)),
                            "y": pivot[col].values,
                            "type": "bar",
                            "name": str(col),
                        }
                        for col in pivot.columns
                    ],
                    "layout": {
                        "title": "Weekly Distance by Sport (Stacked)",
                        "barmode": "stack",
                        "xaxis": {"title": "Week"},
                        "yaxis": {"title": "Total Distance (km)"},
                        "legend": {"orientation": "h", "y": -0.2},
                    },
                }
            ),
        sizing_mode="stretch_width"
    ),
)

df_months = df.groupby(pd.Grouper(key="Activity Date", freq="ME"))["Distance"].sum()
df_months2 = df.resample("1W", on="Activity Date", offset="1W").agg({"Distance": "sum", "Max Speed": "max"})
df_month3 = df.groupby([pd.Grouper(key="Activity Date", freq="W-MON"), "Sport"])["Distance"].sum()

row2 = pn.Row(
    pn.pane.DataFrame(df_months),
    pn.pane.DataFrame(df_months2),
    # pn.pane.ECharts({
    #     "tooltip": {
    #         "trigger": 'axis',
    #         "axisPointer": {
    #             "type": 'shadow'
    #         }
    #     },
    #     "xAxis": {
    #         "data": df_months2.reset_index()['Activity Date'].apply(lambda x: x.strftime("%d %b %Y"))
    #     },
    #     "yAxis":{},
    #     "series": [{
    #         "type": "bar",
    #         "data": df_months2['Distance'].values.tolist()
    #     },
    #     {
    #         "type": "line",
    #         "yAxisIndex": 1,
    #         "data": df_months2['Max Speed'].values.tolist()
    #     }],
    #     "yAxis": [
    #         {
    #             "type": 'value',
    #             "name": 'Distance (km)',
    #         },
    #         {
    #             "type": 'value',
    #             "name": 'Max Speed (km/h)',
    #         }
    #     ]
    # # }, options={"opts": {"renderer":"svg"}
    # }, sizing_mode="stretch_width", height=500)
    pn.pane.ECharts(df.groupby([pd.Grouper(key="Activity Date", freq="W-MON"), "Sport"])["Distance"]
            .sum()
            .reset_index()
            .pivot(index="Activity Date", columns="Sport", values="Distance")
            .fillna(0)
            .pipe(
                lambda pivot: {
                    "data": [
                        {
                            # shift week labels one week earlier so each bar represents the week starting a week before
                            "x": (pivot.index - pd.Timedelta(weeks=1)),
                            "y": pivot[col].values,
                            "type": "bar",
                            "name": str(col),
                        }
                        for col in pivot.columns
                    ],
                    "layout": {
                        "title": "Weekly Distance by Sport (Stacked)",
                        "barmode": "stack",
                        "xaxis": {"title": "Week"},
                        "yaxis": {"title": "Total Distance (km)"},
                        "legend": {"orientation": "h", "y": -0.2},
                    },
                }
            ), sizing_mode="stretch_width", height=500)
)

print(locale.getlocale())

from time import strftime, gmtime

print(strftime("%B %b", gmtime()))

print(df_months)
print(df_months.reset_index()['Activity Date'].apply(lambda x: x.month_name(locale="fr_FR.UTF-8") + x.strftime(" %Y")))
print(df_months.values.tolist())


def build_metric_bar_echart(dataframe, metric="Distance", freq="ME"):
    metric_key = metric.strip().lower()
    metric_map = {
        "distance": {
            "column": "Distance",
            "label": "Distance (km)",
            "transform": lambda s: (s / 1000).round(2),
        },
        "elapsed time": {
            "column": "Elapsed Time",
            "label": "Elapsed Time (h)",
            "transform": lambda s: (s / 3600).round(2),
        },
        "total elevation gain": {
            "column": "Total Elevation Gain",
            "label": "Total Elevation Gain (m)",
            "transform": lambda s: s.round(0),
        },
        "nombre d'activité": {
            "column": None,
            "label": "Nombre d'activités",
            "transform": lambda s: s.astype(int),
        },
    }

    if metric_key not in metric_map:
        raise ValueError(
            "metric must be one of: Distance, Elapsed time, Total Elevation gain, Nombre d'activité"
        )

    config = metric_map[metric_key]
    grouper = pd.Grouper(key="Activity Date", freq=freq)

    if config["column"] is None:
        grouped = dataframe.groupby([grouper, "Sport"]).size().unstack(fill_value=0)
    else:
        grouped = (
            dataframe.groupby([grouper, "Sport"])[config["column"]]
            .sum()
            .unstack(fill_value=0)
        )

    grouped = config["transform"](grouped.fillna(0))

    if freq == "D":
        labels = grouped.index.strftime("%Y-%m-%d").tolist()
    elif freq == "W-MON":
        labels = grouped.index.strftime("%Y-W%W").tolist()
    elif freq == "YE":
        labels = grouped.index.strftime("%Y").tolist()
    else:
        labels = grouped.index.strftime("%Y-%m").tolist()

    return {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "shadow"},
        },
        "legend": {
            "type": "scroll",
            "top": 0,
        },
        "xAxis": {
            "type": "category",
            "data": labels,
        },
        "yAxis": {
            "type": "value",
            "name": config["label"],
        },
        "series": [
            {
                "type": "bar",
                "stack": "total",
                "name": str(sport),
                "data": grouped[sport].tolist(),
            }
            for sport in grouped.columns
        ],
    }

@pn.depends(metric_selector.param.value, interval_selector.param.value)
def metric_bar_chart(metric_value, interval_value):
    freq_map = {
        "Jours": "D",
        "Semaines": "W-MON",
        "Mois": "ME",
        "Années": "YE",
    }

    return pn.pane.ECharts(
        build_metric_bar_echart(df, metric=metric_value, freq=freq_map[interval_value]),
        options={"opts": {"renderer": "svg"}},
        height=400,
        sizing_mode="stretch_width",
    )

ec2 = {
    "tooltip": {
        "trigger": 'axis',
        "axisPointer": {
            "type": 'shadow'
        }
    },
    "xAxis":{
        "data": df_month3.reset_index()['Activity Date'].apply(lambda x: x.strftime("%d-%m"))#x.month_name(locale="fr_FR.UTF-8") + x.strftime(" %Y"))
    },
    "yAxis":{},
    "series": [{
        "type": "bar",
        "data": df_month3.values.astype(int).tolist()
    }]
}

row3 = pn.Column(
    pn.Row(
        metric_selector,
        interval_selector,
    ),
    metric_bar_chart,
    # pn.pane.ECharts(ec2, options={"opts": {"renderer":"svg"}}, height=400, sizing_mode="stretch_width"),
)

def test():
    grouper = pd.Grouper(key="Activity Date", freq="ME")
    dff = df.groupby([grouper, "Sport"]).size().unstack(fill_value=0)
    return dff

row4 = pn.Row(
    pn.pane.DataFrame(test())
)

row5 = pn.Row(
    pn.pane.ECharts(
        {
            "title": {"text": f"Durée par semaine", "left": "center"},
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": df.groupby(pd.Grouper(key="Activity Date", freq="W-MON"))["Moving Time"].sum().index.strftime("%d-%m").tolist(),
                "axisLabel": {"rotate": 45},
            },
            "yAxis": {"type": "value", "name": "Durée (h)"},
            "series": [
                {
                    "type": "bar",
                    "data": [round(v,1) for v in df.groupby(pd.Grouper(key="Activity Date", freq="W-MON"))["Moving Time"].sum()],
                    "itemStyle": {"color": "#fc4c02"},  # Strava orange
                }
            ],
            "grid": {"bottom": 80},
        },
        sizing_mode="stretch_both",
    ),
    pn.pane.ECharts(
        {
            # "title": {"text": "Répartition des activités par sport"},
            "tooltip": {"trigger": "item"},
            # "legend": {"orient": "vertical", "left": "right", "top": "middle"},
            "series": [
                {
                    "name": "Activités",
                    "type": "pie",
                    "radius": ["40%", "70%"],
                    "center": ["55%", "55%"],
                    "data": [
                        {"value": count, "name": sport}
                        for sport, count in df["Sport"].value_counts().items()
                    ],
                    "emphasis": {
                        "itemStyle": {
                            "shadowBlur": 10,
                            "shadowOffsetX": 0,
                            "shadowColor": "rgba(0, 0, 0, 0.5)"
                        }
                    }
                }
            ]
        },
        # height=300,
        sizing_mode="stretch_both",
        ),
        height=300,
)

row6 = pn.pane.Perspective(
            df,
            plugin="d3_y_bar",
            columns=["temps"],
            group_by=["days"],
            split_by=["Sport"],
            # sort=[["Activity Date", "asc"]],
            expressions={
                "distance_km": '"Distance"/1000', "temps": '"Elapsed Time"/60',
                "days": 'bucket("Activity Date", \'D\')',
                "weeks": 'bucket("Activity Date", \'W\')',
                "months": 'bucket("Activity Date", \'M\')',
                "years": 'bucket("Activity Date", \'Y\')',
            },
            height=300, sizing_mode="stretch_width",
            settings=False,
            # title="Activités par sport (temps en minutes)"
        )

pages = [
    ("Résumé global", pn.Column(create_summary_row(df), row5, row3, row4, row6)),
    ("Raw data", pn.pane.DataFrame(df, sizing_mode="stretch_width")),
    ("Raw data (perspective)", pn.pane.Perspective(df))
]

def page(page_name):
    # return pages[page_name][0]
    return pages[page_name][1]

sidebar = create_sidebar(pages=pages, dataframe=df)

# tabs = pn.Tabs( ("Résumé global", pn.Column(summary_row, row1, row2, row3)), dynamic=True, tabs_location="left", sizing_mode="stretch_both")
# tabs = pn.Tabs(*pages, dynamic=True, tabs_location="left", sizing_mode="stretch_both")

pn.template.FastListTemplate(
    title="Strava analyzer",
    main = [create_summary_row(df), row5, row3, row4, row6, pn.pane.Perspective(df, sizing_mode="stretch_width", height=600)],
    # main = pn.bind(page, sidebar[1]),
    # main_layout=None,
    sidebar = sidebar,
    sidebar_width = 250,
    accent = "#FC5200",
).servable()
