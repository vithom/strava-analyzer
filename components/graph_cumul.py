import pandas as pd
import panel as pn


def create_graph_cumul(dataframe):

    def build_cumul_echart():
        df = dataframe.copy()
        df["Year"] = df["Activity Date"].dt.year
        df["DayOfYear"] = df["Activity Date"].dt.dayofyear

        years = sorted(df["Year"].unique())

        series = []
        for year in years:
            df_year = df[df["Year"] == year].copy()
            daily = (
                df_year.groupby("DayOfYear")["Elapsed Time"]
                .sum()
                .reindex(range(1, 367), fill_value=0)
            )
            cumul_hours = (daily.cumsum() / 3600).round(2)

            series.append({
                "type": "line",
                "name": str(year),
                "data": cumul_hours.tolist(),
                "smooth": True,
                "symbol": "none",
            })

        # Générer des labels de dates lisibles (référence année bissextile)
        date_labels = [
            (pd.Timestamp("2024-01-01") + pd.Timedelta(days=d - 1)).strftime("%#d %b")
            for d in range(1, 367)
        ]

        # Positions des 1ers de chaque mois pour l'axe
        month_first_days = [
            pd.Timestamp(year=2024, month=m, day=1).dayofyear - 1
            for m in range(1, 13)
        ]

        return {
            "tooltip": {
                "trigger": "axis",
            },
            "legend": {
                "type": "scroll",
                "top": 0,
            },
            "xAxis": {
                "type": "category",
                "data": date_labels,
                "axisLabel": {
                    "interval": 30,
                    "rotate": 45,
                },
                "axisTick": {"alignWithLabel": True},
            },
            "yAxis": {
                "type": "value",
                "name": "Temps cumulé (h)",
            },
            "series": series,
            "grid": {"bottom": 80, "right": 40},
        }

    return pn.Column(
        pn.pane.ECharts(
            build_cumul_echart(),
            options={"opts": {"renderer": "svg"}},
            height=400,
            sizing_mode="stretch_width",
        ),
    )
