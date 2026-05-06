import panel as pn
# from pyecharts.charts import Line, Pie, Calendar
# from pyecharts import options as opts
import json

# Activation de l'extension Panel
pn.extension('echarts')

# --- 1. FONCTIONS GÉNÉRATRICES DE PAGES ---
# Ces fonctions simulent tes différentes vues. 
# C'est ici que tu utiliseras tes données stravalib.

def page_generale():
    # Exemple de graphique ECharts (Calendrier)
    # chart = (
    #     Calendar()
    #     .add("", [["2024-01-01", 10], ["2024-01-02", 20]], calendar_opts=opts.CalendarOpts(range_="2024"))
    #     .set_global_opts(title_opts=opts.TitleOpts(title="Intensité Annuelle"))
    # )
    
    return pn.Column(
        "# 📊 Vue d'ensemble",
        pn.Row(
            pn.indicators.Number(name="Activités", value=142, font_size='24pt'),
            pn.indicators.Number(name="Distance Totale (km)", value=2450, font_size='24pt'),
        ),
        # pn.pane.ECharts(chart, height=400, sizing_mode="stretch_width"),
        sizing_mode="stretch_width"
    )

def page_running():
    return pn.Column(
        "# 🏃 Course à pied",
        "Statistiques spécifiques : PR, Allures, Usure des chaussures...",
        # Ton graphique ECharts ici
        sizing_mode="stretch_width"
    )

def page_cycling():
    return pn.Column(
        "# 🚴 Cyclisme",
        "Statistiques spécifiques : FTP, Dénivelé, Rapport W/kg...",
        sizing_mode="stretch_width"
    )

def page_settings():
    return pn.Column(
        pn.Card("# ⚙️ Paramètres"),
        pn.widgets.PasswordInput(name="Strava Client Secret", placeholder="Entrez votre secret"),
        pn.widgets.Button(name="Rafraîchir les données", button_type="primary"),
        sizing_mode="stretch_width"
    )

# --- 2. LOGIQUE DE NAVIGATION ---

# Le sélecteur dans la sidebar
page_selector = pn.widgets.Select(
    name="Navigation", 
    options={
        "🏠 Général": "general",
        "🏃 Course à pied": "run",
        "🚴 Cyclisme": "bike",
        "⚙️ Paramètres": "settings"
    }
)

# Fonction de routage qui retourne le contenu de la page
@pn.depends(page_selector)
def render_page(selection):
    if selection == "general":
        return page_generale()
    elif selection == "run":
        return page_running()
    elif selection == "bike":
        return page_cycling()
    elif selection == "settings":
        return page_settings()

# --- 3. TEMPLATE ET MISE EN PAGE ---

template = pn.template.FastListTemplate(
    title="Mon Strava Dashboard",
    sidebar=[
        "### Menu",
        page_selector,
        pn.pane.Markdown("---"),
        "**Statut API :** 🟢 Connecté"
    ],
    sidebar_footer="© 2024 Mon Strava Dashboard",
    main=[
        render_page
    ],
    accent_base_color="#FC4C02",  # Couleur Orange Strava
    header_background="#FC4C02",
)

template.servable()