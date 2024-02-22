from flask import Flask, jsonify, render_template, request
from flask_apscheduler import APScheduler
from model.model import predict_passangers
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
    #daily_data_update()
    json_data = forecast()
    json_data = json_data.get_json()
    return render_template('index.html', prediction=json_data['prediction'], actual=json_data['actual'])

def forecast():
    predictions = []
    prediction_dates = []
    actual_passangers = []
    actual_days = []
    with open('./data/weather_forecast.csv', 'r') as f:
        next(f)
        data = f.readlines()
        for i, line in enumerate(data):
            line = line.strip().split(',')
            prediction_dates.append(line[2] + '-' + line[3] + '-' + line[4])
            holi = is_holiday(int(line[2]), int(line[3]), int(line[4]), 'FI') 
            day_of_week = datetime.datetime(int(line[4]), int(line[3]), int(line[2])).weekday()
            predictions.append(predict_passangers(float(line[0]), float(line[1])/100, line[2], line[3], day_of_week, holi))

    with open('./data/past_passanger_data_merged.csv', 'r') as f:
        data = f.readlines()[5:]
        for i, line in enumerate(data):
            line = line.strip().split(';')
            actual_days.append(line[0])
            actual_passangers.append(line[1])

    return jsonify({'actual': {'date': actual_days, 'passangers': actual_passangers},  'prediction': {'predictions': predictions, 'dates': prediction_dates}}) 

def is_holiday(day, month, year, country):
    holiday = CountryHoliday(country)
    if datetime.date(year, month, day) in holiday:
        return 1
    else:
        return 0

def weather_forecast():
    response = requests.get('https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&hourly=temperature_2m,rain&past_days=5')
    data = response.json()
    df = pd.DataFrame(data['hourly'])
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df_daily = df.resample('D').agg({'temperature_2m': 'mean', 'rain': 'sum'})
    print(df_daily.head())
    df_daily['day'] = df_daily.index.day
    df_daily['month'] = df_daily.index.month
    df_daily['year'] = df_daily.index.year
    df_daily.to_csv('./data/weather_forecast.csv', index=False)


def past_passanger_data():
    current_weeK = datetime.datetime.now().isocalendar()[1]
    current_year = datetime.datetime.now().isocalendar()[0]
    last_week, last_year = 0, current_year
    if current_weeK == 1:
        last_week = 52
        last_year = current_year - 1
    else:
        last_week = current_weeK - 1
    print(current_weeK)
    def test(week, year):
        url_start = 'https://hsl.louhin.com/api/1.0/data/257001?LWSAccessKey=d59c041a-2ad1-4beb-b769-b9d7ea3a5628&filter[VIIKKO]='
        url_start = url_start + str(week) + '&filter[VUOSI]=' + str(year)
        return url_start
    resp_current_week = requests.get(test(current_weeK, current_year))
    resp_last_week = requests.get(test(last_week, last_year))
    with open('./data/past_passanger_data.csv', 'w', encoding='utf-8') as f:
        f.write(resp_current_week.text)

    with open('./data/past_passanger_data_2_last.csv', 'w', encoding='utf-8') as f:
        f.write(resp_last_week.text)

def clean_data():
    df = pd.read_csv('./data/past_passanger_data.csv', delimiter=';', parse_dates=['PÃIVÃMÃÃRÃ'])
    df_2 = pd.read_csv('./data/past_passanger_data_2_last.csv', delimiter=';', parse_dates=['PÃIVÃMÃÃRÃ'])

    df['PÃIVÃMÃÃRÃ'] = df['PÃIVÃMÃÃRÃ'].dt.date
    df_2['PÃIVÃMÃÃRÃ'] = df_2['PÃIVÃMÃÃRÃ'].dt.date

    df_merged = pd.concat([df, df_2])

    df_grouped = df_merged.groupby('PÃIVÃMÃÃRÃ')['NOUSIJAT'].sum().reset_index()
    df_grouped = df_grouped.sort_values('PÃIVÃMÃÃRÃ')
    df_grouped.to_csv('./data/past_passanger_data_merged.csv', index=False, sep=';')

def daily_data_update():
    weather_forecast()
    past_passanger_data()
    clean_data()

@scheduler.task('cron', id='do_job_1', hour='0', minute='30')
def scheduled_job():
    daily_data_update()

if __name__ == '__main__':
    daily_data_update()
    app.run()
