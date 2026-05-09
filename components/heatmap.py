from PIL.ImageShow import show
import pandas as pd
import panel as pn

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
            # "formatter": "{a}: {c} activités<br/>{b}"
        },
        # "visualMap": {
        #     "min": 0,
        #     "max": activity_counts['count'].max() if not activity_counts.empty else 0
        # },
        "calendar": {
            # "orient": "vertical",
            "range": [activity_counts['date_str'].min(), activity_counts['date_str'].max()],
            "dayLabel": {
                "firstDay": 1,
                "nameMap": ["Di", "Lu", "Ma", "Me", "Je", "Ve", "Sa"]
            },
            "monthLabel": {
                "nameMap": ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
            }
        },
        "series": {
            "type": "heatmap",
                "label": {"show": "true"},
            "coordinateSystem": "calendar",
            "data": data
        }
    }

    return pn.Row(pn.pane.ECharts(config, sizing_mode="stretch_both"))

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
            # "position": "top",
            # "formatter": "{b}: {c} activités"
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
            # "left": 30,
            # "right": 30,
            # "cellSize": ["auto", 13],
            "range": "2025",
            "itemStyle": {
                # "borderWidth": 0.5,
                "borderColor": ""
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
    
    return pn.pane.ECharts(config, sizing_mode="stretch_both")