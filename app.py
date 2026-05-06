import pandas as pd
import panel as pn
import plotly.graph_objs as go
import locale

from tornado import template

from data import get_data, get_data_csv

from pages.home import HomePage

from components.summary import create_summary_row
from components.sidebar import create_sidebar
from components.bargraph import create_bargraph

pn.extension('perspective', 'echarts')

# df = get_data_csv()
df = get_data()

# print(df.groupby(df["Activity Date"].dt.weekday)["Distance"].sum().reset_index().rename(columns={"Activity Date": "Month", "Distance": "Total Distance (km)"}))

dff = df[["Activity Date", "Activity Name", "Sport", "Elapsed Time"]].groupby("Sport")["Elapsed Time"].sum()

df_months = df.groupby(pd.Grouper(key="Activity Date", freq="ME"))["Distance"].sum()
df_months2 = df.resample("1W", on="Activity Date", offset="1W").agg({"Distance": "sum", "Max Speed": "max"})
df_month3 = df.groupby([pd.Grouper(key="Activity Date", freq="W-MON"), "Sport"])["Distance"].sum()

row2 = pn.Row(
    pn.pane.DataFrame(df_months),
    pn.pane.DataFrame(df_months2),
    pn.pane.DataFrame(df_month3),
)

print(df_months)
print(df_months.reset_index()['Activity Date'].apply(lambda x: x.month_name(locale="fr_FR") + x.strftime(" %Y")))
print(df_months.values.tolist())

def test():
    grouper = pd.Grouper(key="Activity Date", freq="ME")
    dff = df.groupby([grouper, "Sport"]).size().unstack(fill_value=0)
    return dff

row4 = pn.pane.DataFrame(test())

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
    ("Résumé global", HomePage(df=df)),
    ("Raw data", pn.pane.DataFrame(df, sizing_mode="stretch_width")),
    ("Raw data (perspective)", pn.Row(pn.pane.Perspective(df, sizing_mode="stretch_both"), styles={"min-height": "600px"})),
]

# def test():
#     return [create_summary_row(df), row5, create_bargraph(df), row4, row6, pn.pane.Perspective(df, sizing_mode="stretch_width", height=600)]

sidebar, page_selector = create_sidebar(pages=pages, dataframe=df)

@pn.depends(page_selector)
def render_pages(name):
    # print(type(template.main.objects[1]))
    # template.main.clear()
    # template.main[0].objects = [pages_test[name.new].view()]
    return pages[name][1]
    # return pages_test[name].view()

# watcher = page_selector.param.watch(render_pages, "value")

template = pn.template.FastListTemplate(
    title="Strava analyzer",
    # main = [create_summary_row(df), row5, row2, create_bargraph(df), row4, row6, pn.pane.Perspective(df, sizing_mode="stretch_width", height=600)],
    # main = pn.bind(page, sidebar[1]),
    # main = pn.bind(page_test, page_selector),
    # main = [pages_test["home"]],
    main = [render_pages],
    # main = page(0),
    # main_layout=None,
    sidebar = [sidebar],
    sidebar_width = 250,
    shadow = True,
    # neutral_color="#FFFFFF",
    accent = "#FC5200",
)

# template.main.append(pn.pane.Markdown("Contenu de la page principale"))

template.servable()
