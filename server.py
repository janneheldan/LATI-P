from flask import Flask, jsonify, render_template, request
from flask_apscheduler import APScheduler
from model import predict_passangers
import pandas as pd
import datetime
from holidays import CountryHoliday 
import requests

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route('/', methods=['GET'])
def index():
    predictions = []
    with open('weather_forecast.csv', 'r') as f:
        next(f)
        data = f.readlines()
        for i, line in enumerate(data):
            line = line.strip().split(',')
            holi = is_holiday(int(line[2]), int(line[3]), int(line[4]), 'FI') 
            day_of_week = datetime.datetime(int(line[4]), int(line[3]), int(line[2])).weekday()
            predictions.append({'x': i + 1, 'y': predict_passangers(float(line[0]), float(line[1])/100, line[2], line[3], day_of_week, holi)})

    print(predictions)
    return render_template('index.html', predictions=predictions)


@app.route('/predict', methods=['GET'])
def predict_get():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict_post():
    date = request.form.get('date')
    temp = request.form.get('temp')
    rain = request.form.get('water')

    # Split the date string into year, month, and day
    date_parts = date.split('-')
    year = int(date_parts[0])
    month = int(date_parts[1])
    day = int(date_parts[2])

    day_of_week = datetime.datetime(year, month, day).weekday()

    h = is_holiday(day, month, year, 'FI')

    print(temp, rain, day, month, day_of_week, h)

    prediction = predict_passangers(float(temp), float(rain)/100, int(day), int(month), day_of_week, h)

    return render_template('predict.html', prediction=prediction)

def is_holiday(day, month, year, country):
    holiday = CountryHoliday(country)
    if datetime.date(year, month, day) in holiday:
        return 1
    else:
        return 0

def weather_forecast():
    response = requests.get('https://api.open-meteo.com/v1/forecast?latitude=60.1695&longitude=24.9354&hourly=temperature_2m,rain')
    data = response.json()
    df = pd.DataFrame(data['hourly'])
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df_daily = df.resample('D').agg({'temperature_2m': 'mean', 'rain': 'sum'})
    df_daily['day'] = df_daily.index.day
    df_daily['month'] = df_daily.index.month
    df_daily['year'] = df_daily.index.year
    df_daily.to_csv('weather_forecast.csv', index=False)

def get_data():
    print("Getting data...")


@scheduler.task('cron', id='do_job_1', hour='0', minute='30')
def scheduled_job():
    get_data()

if __name__ == '__main__':
    app.run(debug=True)
