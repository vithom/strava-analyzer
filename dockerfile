FROM python:3.13-alpine

WORKDIR /opt

COPY requirements.txt app.py .strava.secrets ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5006
CMD ["panel", "serve", "app.py"]