FROM python:3.13-alpine

WORKDIR /opt

COPY requirements.txt app.py .strava.secrets data.py ./
COPY components/summary.py ./components/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5006
CMD ["panel", "serve", "--dev", "app.py", "--allow-websocket-origin=*"]
