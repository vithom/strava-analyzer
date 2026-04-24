import pandas as pd
import panel as pn
import plotly.graph_objs as go
import locale
import os

from datetime import datetime
from data import get_data

pn.extension('perspective', 'plotly', 'echarts')


# activity_mapping = {
#     "Run": "Course",
#     "Walk": "Marche",
#     "Swim": "Natation",
#     "Ride": "Vélo",
#     "Hike": "Randonnée",
#     "MountainBikeRide": "VTT",
#     "Yoga": "Yoga",
#     "TrailRun": "Trail",
#     "AlpineSki": "Ski alpin"
# }


df = get_data()

activity_types = df["Sport"].unique()

total_dist = df["Distance"].sum()
total_time = df["Elapsed Time"].sum()
total_days_on_strava = (datetime.now() - df.tail(1)["Activity Date"].iloc[0].replace(tzinfo=None)).days

# print(df.groupby(df["Activity Date"].dt.weekday)["Distance"].sum().reset_index().rename(columns={"Activity Date": "Month", "Distance": "Total Distance (km)"}))

dff = df[["Activity Date", "Activity Name", "Sport", "Elapsed Time"]].groupby("Sport")["Elapsed Time"].sum()

#graphs
# * Distance / activité / mois



# component = pn.pane.panel(dff)

# summary_vega = {
#     "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
#     "data": {"data": activities },
#
#     # "layer": [
#     #     {
#     #         "mark": "bar",
#     #
#     #     }
#     # ]
# }

def big(name, value):
    return pn.widgets.Number(name=name, value=value, font_size="40pt")


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



summary_row = pn.Column(
    pn.FlexBox(
        big("Activités", len(df)),
        big("Jours", total_days_on_strava),
        big("Distance", round(total_dist/1000)),
        big("Dénivelé", round(df["Total Elevation Gain"].sum())),
        big("Heures de sport", round(total_time/3600)),
        big("Heures en mouvement", round(df["Moving Time"].sum()/3600)),
        # big("Vitesse moyenne", round(df["Average Speed"].mean()*3.6, 1)),
        justify_content="space-around", gap="16px"
    ),

        pn.pane.Perspective(
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
            title="Activités par sport (temps en minutes)"
        ),

        # pn.pane.Vega(summary_vega),

        pn.Row(
            metric_selector,
            interval_selector,
        ),
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

row3 = pn.Row(
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

# tabs = pn.Tabs( ("Résumé global", pn.Column(summary_row, row1, row2, row3)), dynamic=True, tabs_location="left", sizing_mode="stretch_both")
tabs = pn.Tabs( ("Résumé global", pn.Column(summary_row, row3, row4)), dynamic=True, tabs_location="left", sizing_mode="stretch_both")
for a in activity_types:
    tabs.append( (f"# {a}", pn.Column()) )

tabs.append(("Raw data", pn.pane.DataFrame(df, sizing_mode="stretch_width")))
tabs.append(("Raw data (perspective)", pn.pane.Perspective(df, sizing_mode="stretch_both")))

pn.template.FastListTemplate(
    title="Strava analyzer",
    # main = [summary_row, row2, row3, pn.pane.Perspective(df, sizing_mode="stretch_both")],
    main = tabs,
    # accent = "orange",
    accent = "#FC5200"
).servable()
