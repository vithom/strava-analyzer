import panel as pn
import pandas as pd

from datetime import datetime

# pn.extension(css_files=["https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"])

def big(name, value, unit=""):
    format = "{value} " + unit if unit else "{value}"
    return pn.widgets.Number(name=name, value=value, format=format, font_size="40pt")

def metric_card(content, color="grey"):
    return pn.pane.HTML(f"""
    <div style="background-color: #f0f0f0; border-radius: 8px; padding: 8px 16px; border-left: 4px solid {color};">
        <div style="font-size: 24px; color: grey;">{content}</div>
    </div>
    """)

def metric(name, value, icon=None):
    pn.extension(css_files=["https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"])
    
    INDICATOR_TEMPLATE = """
    <div style="text-align:center; padding:10px;">
        <span class="material-symbols-outlined" style="font-size:36px;">{icon}</span>
        <div style="font-size:40px; font-weight:bold;">{value}</div>
        <div style="font-size:14px; color:gray;">{name}</div>
    </div>
    """
    html = pn.pane.HTML(
        pn.rx(INDICATOR_TEMPLATE.format)(icon=icon or "", value=value, name=name),
        # sizing_mode="fixed", width=200, height=130,
    )
    return html

def create_summary_row(df: pd.DataFrame):
    total_distance = df["Distance"].sum()
    total_time = df["Elapsed Time"].sum()
    total_elevation = df["Total Elevation Gain"].sum()
    total_days_on_strava = (datetime.now() - df.tail(1)["Activity Date"].iloc[0].replace(tzinfo=None)).days
    unique_sports = df["Sport"].unique()
    
    return pn.Column(

        pn.FlexBox(
            metric("Activités", len(df), icon="directions_run"),
            metric("Distance (km)", round(total_distance/1000), icon="map"),
            metric("Temps (h)", round(total_time/3600), icon="schedule"),
            metric("Dénivelé (m)", round(total_elevation), icon="terrain"),
            metric("FC max (bpm)", round(df['Max Heart Rate'].max()), icon="favorite"),
            justify_content="space-around",
        ),
        # metric_card(
        #     f"{len(df)} activités depuis {total_days_on_strava} jours sur {len(unique_sports)} sports",
        #     color="#fc5200"
        # ),

        # pn.layout.Divider(),

        # pn.FlexBox(
        #     big("📊 Activités", len(df)),
        #     big("🛣️ Distance (km)", round(total_distance/1000)),
        #     big("⏱️ Temps (h)", round(df['Moving Time'].sum()/3600)),
        #     big("📈 Dénivelé (m)", round(total_elevation)),
        #     big("💗 FC max", round(df['Max Heart Rate'].max())),

        #     justify_content="space-evenly",
        #     # sizing_mode="stretch_width"
        # ),
    )