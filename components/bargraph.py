import pandas as pd
import panel as pn


def create_bargraph(dataframe):
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

    def build_metric_bar_echart(metric="Distance", freq="ME"):
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
            build_metric_bar_echart(metric=metric_value, freq=freq_map[interval_value]),
            options={"opts": {"renderer": "svg"}},
            height=400,
            sizing_mode="stretch_width",
        )

    return pn.Column(
        pn.Row(metric_selector, interval_selector),
        metric_bar_chart,
    )
