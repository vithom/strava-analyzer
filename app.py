from datetime import datetime

import dotenv
import pandas as pd
import panel as pn
import plotly.graph_objs as go
import locale
import os

from bokeh.settings import settings
from dotenv import load_dotenv
from pandas.core.computation import expressions

load_dotenv(".strava.secrets")

print(os.environ.get("STRAVA_CLIENT_ID"))
print(os.environ.get("STRAVA_CLIENT_SECRET"))


from stravalib import Client

client = Client(
    access_token=os.environ.get("ACCESS_TOKEN"),
    refresh_token=os.environ.get("REFRESH_TOKEN"),
    token_expires=int(os.environ.get("EXPIRES_AT"))
)

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

activities = client.get_activities()

for i,a in enumerate(activities):
    print(type(a))
    if i > 2:
        break

df = pd.DataFrame([
    {
        "Activity Name": a.name,
        "Activity Date": a.start_date_local,
        "Sport": a.sport_type.root,
        "Distance": a.distance,
        "Moving Time": a.moving_time,
        "Elapsed Time": a.elapsed_time,
        "Total Elevation Gain": a.total_elevation_gain,
        "Average Speed": a.average_speed,
        "Max Speed": a.max_speed,
        "Average cadence": a.average_cadence,
        "Average heart rate": a.average_heartrate,
        "Max heart rate": a.max_heartrate,
        "Average power": a.average_watts,
    }
    for a in activities
])

print(df["Elapsed Time"].sum())

activity_types = df["Sport"].unique()


print(f"refresh_token={client.refresh_token}")

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

summary_row = pn.Column(
    pn.FlexBox(
        pn.widgets.Number(name="Activités", value=len(df), disabled=True),
        pn.widgets.Number(name="Jours", value=total_days_on_strava, disabled=True),
        pn.widgets.Number(name="Distance", value=round(total_dist/1000), disabled=True),
        pn.widgets.Number(name="Heures", value=round(total_time/3600), disabled=True),
        pn.widgets.Number(name="Dénivelé", value=round(df["Total Elevation Gain"].sum()), disabled=True),
        justify_content="space-around", gap="16px"
    ),

        pn.pane.Perspective(
            df,
            plugin="d3_y_bar",
            columns=["temps"],
            split_by=["Sport"],
            sort=[["Activity Date", "asc"]],
            expressions={"distance_km": '"Distance"/1000', "temps": '"Elapsed Time"/60'},
            height=300, sizing_mode="stretch_width",
            settings=False,
            title="Activités par sport (temps en minutes)"
        ),

        # pn.pane.Vega(summary_vega),

        pn.Row(
            pn.widgets.RadioButtonGroup(name="value type", options=['Occurence','Temps de pratique', 'Distance', 'Dénivelé'], button_style="outline", button_type="primary"),
            pn.widgets.RadioButtonGroup(name="interval", options=['Jours', 'Semaines', 'Mois', 'Années'], button_style="outline", button_type="primary"),
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

echart_bar = {
    "tooltip": {
        "trigger": 'axis',
        "axisPointer": {
            "type": 'shadow'
        }
    },
    "xAxis": {
        "data": df_months.reset_index()['Activity Date'].apply(lambda x: x.month_name(locale="fr_FR.UTF-8") + x.strftime(" %Y"))
    },
    "yAxis":{},
    "series": [{
        "type": "bar",
        "data": df_months.values.tolist()
    }]
}

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
    pn.pane.ECharts(echart_bar, options={"opts": {"renderer":"svg"}}, height=400, sizing_mode="stretch_width"),
    pn.pane.ECharts(ec2, options={"opts": {"renderer":"svg"}}, height=400, sizing_mode="stretch_width"),
)

tabs = pn.Tabs( ("Résumé global", pn.Column(summary_row, row1, row2, row3)), dynamic=True, tabs_location="left", sizing_mode="stretch_both")
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
