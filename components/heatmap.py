import pandas as pd
import panel as pn

def create_heatmap(df):
    """
    Crée une heatmap de type calendrier affichant le nombre d'activités par jour de l'année (comme GitHub).
    Utilise les données de 2025.
    """
    # Copier et filtrer pour 2025
    df_copy = df.copy()
    df_2025 = df_copy[df_copy['Activity Date'].dt.year == 2025]
    
    # Ajouter une colonne de date en string
    df_2025['date_str'] = df_2025['Activity Date'].dt.strftime('%Y-%m-%d')
    
    # Grouper par date, compter les activités
    activity_counts = df_2025.groupby('date_str').size().reset_index(name='count')
    
    # Préparer les données pour ECharts : liste de [date, valeur]
    data = [[row['date_str'], row['count']] for _, row in activity_counts.iterrows()]
    
    # Configuration ECharts pour la heatmap calendrier
    config = {
        "title": {"text": "Heatmap des activités par jour (2025)", "left": "center"},
        "tooltip": {
            "position": "top",
            "formatter": "{b}: {c} activités"
        },
        "visualMap": {
            "min": 0,
            "max": activity_counts['count'].max() if not activity_counts.empty else 0,
            "type": "piecewise",
            "orient": "horizontal",
            "left": "center",
            "top": 30,
            "pieces": [
                {"min": 0, "max": 0, "color": "#ebedf0"},  # Gris clair pour 0
                {"min": 1, "max": 1, "color": "#9be9a8"},  # Vert clair
                {"min": 2, "max": 3, "color": "#40c463"},  # Vert
                {"min": 4, "max": 5, "color": "#30a14e"},  # Vert foncé
                {"min": 6, "color": "#216e39"}  # Vert très foncé
            ],
            "showLabel": True
        },
        "calendar": {
            "top": 120,
            "left": 30,
            "right": 30,
            # "cellSize": ["auto", 13],
            "range": ["2025-08","2026-05-06"],
            "itemStyle": {
                "borderWidth": 0.5,
                "borderColor": "#111"
            },
            "yearLabel": {"show": False},
            "monthLabel": {
                "show": True,
                "nameMap": {
                    "1": "Jan", "2": "Fév", "3": "Mar", "4": "Avr", "5": "Mai", "6": "Jun",
                    "7": "Jul", "8": "Aoû", "9": "Sep", "10": "Oct", "11": "Nov", "12": "Déc"
                }
            },
            "dayLabel": {
                "show": True,
                "nameMap": ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
            }
        },
        "series": {
            "type": "heatmap",
            "coordinateSystem": "calendar",
            "data": data
        }
    }
    
    return pn.Column(pn.pane.ECharts(config, sizing_mode="stretch_both"), pn.pane.DataFrame(activity_counts))