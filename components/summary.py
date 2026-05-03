import panel as pn
import pandas as pd

from datetime import datetime

def big(name, value, unit=""):
    format = "{value} " + unit if unit else "{value}"
    return pn.widgets.Number(name=name, value=value, format=format, font_size="40pt")

def metric_card(content, color="grey"):
    return pn.pane.HTML(f"""
    <div style="background-color: #f0f0f0; border-radius: 8px; padding: 8px 16px; border-left: 4px solid {color};">
        <div style="font-size: 24px; color: grey;">{content}</div>
    </div>
    """)

def create_summary_row(df: pd.DataFrame):
    total_distance = df["Distance"].sum()
    total_time = df["Elapsed Time"].sum()
    total_elevation = df["Total Elevation Gain"].sum()
    total_days_on_strava = (datetime.now() - df.tail(1)["Activity Date"].iloc[0].replace(tzinfo=None)).days
    unique_sports = df["Sport"].unique()
    
    return pn.Column(

        # metric_card(
        #     f"{len(df)} activités depuis {total_days_on_strava} jours sur {len(unique_sports)} sports",
        #     color="#fc5200"
        # ),

        pn.FlexBox(
            big("📊 Activités", len(df)),
            big("🛣️ Distance", round(total_distance/1000), "km"),
            big("⏱️ Temps", round(df['Moving Time'].sum()/3600), "h"),
            big("📈 Dénivelé", round(total_elevation), "m"),
            big("💗 FC max", round(df['Max Heart Rate'].max())),

            justify_content="space-evenly",
            # sizing_mode="stretch_width"
        ),
    )