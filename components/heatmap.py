from PIL.ImageShow import show
import pandas as pd
import panel as pn

DAY_MAP = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
MONTH_MAP = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]

def c_heatmap(df):
    # dff = df[df['Activity Date'].dt.year == 2025]
    dff = df.copy()
    dff['date_str'] = dff['Activity Date'].dt.strftime('%Y-%m-%d')
    activity_counts = dff.groupby('date_str').size().reset_index(name='count')
    data = [[row['date_str'], row['count'], row['count']] for _, row in activity_counts.iterrows()]
    # print(data)
    
    config = {
        "title": {"text": "Heatmap des activités", "left": "center"},
        "tooltip": {
            # "trigger": "axis",
            "formatter": "{a}|{b}|{c}|{d}|{e}"
        },
        # "visualMap": {
        #     "min": 0,
        #     "max": activity_counts['count'].max() if not activity_counts.empty else 0
        # },
        "calendar": {
            # "orient": "vertical",
            "top": 80,
            "range": [activity_counts['date_str'].min(), activity_counts['date_str'].max()],
            "dayLabel": {
                "firstDay": 1,
                "nameMap": DAY_MAP
            },
            "monthLabel": {
                "nameMap": MONTH_MAP
            }
        },
        "series": {
            "type": "heatmap",
            "label": {"show": "true"},
            "coordinateSystem": "calendar",
            "data": data
        }
    }

    return pn.Row(pn.pane.ECharts(config, height=300, width=1200), scroll=True)

def create_heatmap(df):
    """
    Crée une heatmap de type calendrier affichant le nombre d'activités par jour de l'année (comme GitHub).
    Utilise les données de 2025.
    """
    year_select = pn.widgets.Select(
        name="Année",
        options=sorted(df['Activity Date'].dt.year.unique().tolist()),
        value=2026,
    )

    def build_heatmap(year):
        dff = df.copy()
        dff['date_str'] = dff['Activity Date'].dt.strftime('%Y-%m-%d')

        # Déterminer le sport unique ou "Multiples" par jour
        s = dff.groupby('date_str').agg(
            sport_n=("Sport", "count"),
            nunique=("Sport", "nunique"),
            sport_first=("Sport", "first"),
        )
        s["Sport"] = s.apply(
            lambda r: r["sport_first"] if r["nunique"] == 1 else "Multiples", axis=1
        )

        # Couleurs par sport
        sport_colors = {
            "Course": "#fc4c02",
            "Trail": "#e8702a",
            "Marche": "#8bc34a",
            "Randonnée": "#4caf50",
            "Natation": "#2196f3",
            "Vélo de route": "#ff9800",
            "VTT": "#795548",
            "Yoga": "#9c27b0",
            "Ski alpin": "#00bcd4",
            "Multiples": "#757575",
        }

        # Construire les catégories et couleurs à partir des sports présents
        present_sports = sorted(s["Sport"].unique(), key=lambda x: x)
        categories = [sp for sp in present_sports]
        colors = [sport_colors.get(sp, "#999999") for sp in categories]

        dat = [
            {
                "value": [date, row["sport_n"], row["Sport"]],
                "name": f"{date} : {row['sport_n']} activité(s) - {row['Sport']}",
            }
            for date, row in s.iterrows()
        ]

        config = {
            "tooltip": {
                "formatter": "{b}",
            },
            "visualMap": {
                "type": "piecewise",
                "categories": categories,
                "inRange": {"color": colors},
                "orient": "horizontal",
                "left": "center",
                "top": 0,
            },
            "calendar": {
                "top": 70,
                "range": year,
                # "left": 30,
                "yearLabel": {"show": False},
                "dayLabel": {
                    "firstDay": 1,
                    "nameMap": DAY_MAP,
                },
                "monthLabel": {
                    "nameMap": MONTH_MAP,
                },
            },
            "series": {
                "type": "heatmap",
                "coordinateSystem": "calendar",
                "data": dat,
                "label": {
                    "show": True,
                    "formatter": "{@[1]}",
                    # "color": "#000",
                    # "fontSize": 14,
                },
            },
        }
        return pn.pane.ECharts(config, height=300, width=1200)
        
    
    return pn.Column(
        year_select,
        pn.bind(build_heatmap, year_select),
    )