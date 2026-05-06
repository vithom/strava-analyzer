import pandas as pd
import panel as pn
import param

from components.summary import create_summary_row

class HomePage(pn.viewable.Viewer):
    df = param.DataFrame(doc="DataFrame des activités Strava")

    def __panel__(self) -> pn.viewable.Viewable:
        return pn.Column(
            create_summary_row(self.df),
        )