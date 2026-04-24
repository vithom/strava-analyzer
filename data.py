import pandas as pd
import os

from dotenv import load_dotenv
from stravalib import Client

load_dotenv(".strava.secrets")

print(os.environ.get("STRAVA_CLIENT_ID"))
print(os.environ.get("STRAVA_CLIENT_SECRET"))


client = Client(
    access_token=os.environ.get("ACCESS_TOKEN"),
    refresh_token=os.environ.get("REFRESH_TOKEN"),
    token_expires=int(os.environ.get("EXPIRES_AT"))
)

def get_data():

    activities = client.get_activities()

    return pd.DataFrame([
        {
            "Activity Name": a.name,
            "Activity Date": a.start_date_local,
            "Sport": a.sport_type.root,
            "Distance": a.distance,
            "Moving Time": a.moving_time,
            "Elapsed Time": a.elapsed_time,
            "Total Elevation Gain": a.total_elevation_gain,
            "Average Speed": a.average_speed,
            "Max Speed": a.max_speed,
            "Average cadence": a.average_cadence,
            "Average heart rate": a.average_heartrate,
            "Max heart rate": a.max_heartrate,
            "Average power": a.average_watts,
        }
        for a in activities
    ])
