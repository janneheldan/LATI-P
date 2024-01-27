from flask import Flask, jsonify, render_template, request
from flask_apscheduler import APScheduler
from model import predict_passangers
import pandas as pd
import datetime
from holidays import CountryHoliday 

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

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

    print(prediction)
    return render_template('predict.html', prediction=prediction)

def is_holiday(day, month, year, country):
    holiday = CountryHoliday(country)
    if datetime.date(year, month, day) in holiday:
        return 1
    else:
        return 0


def get_data():
    print("Getting data...")


@scheduler.task('cron', id='do_job_1', hour='0', minute='30')
def scheduled_job():
    get_data()

if __name__ == '__main__':
    app.run(debug=True)
