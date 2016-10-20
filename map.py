from flask import Flask, render_template
from urllib.request import Request, urlopen
import json
import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

@app.route('/')
def index():
  feed = get_jsonfeed()
  stations = get_stations(feed)
  startlat=39.9526
  startlng=-75.1652
  pred = predict_demand()
  return render_template('home.html', stations=stations, pred=pred)

@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/data')
def history():
  return render_template('data.html')

@app.route('/test')
def test():
  return render_template('test2.html')

def get_jsonfeed():
  req = Request('https://www.rideindego.com/stations/json/', headers={'User-Agent': 'Mozilla/5.0'})
  data = urlopen(req).read().decode('utf-8')
  feed = json.loads(data)
  return feed


def get_stations(feed):
  nstations = len(feed['features'])
  station_id = [feed['features'][i]['properties']['kioskId'] for i in range(0,nstations)]
  station_name = [feed['features'][i]['properties']['name'] for i in range(0,nstations)]
  station_add = [feed['features'][i]['properties']['addressStreet'] for i in range(0,nstations)]
  lat = [feed['features'][i]['geometry']['coordinates'][1] for i in range(0,nstations)]
  lng = [feed['features'][i]['geometry']['coordinates'][0] for i in range(0,nstations)]
  #ad - available docks, td - total docks, ab - available bikes
  ad = [feed['features'][i]['properties']['docksAvailable'] for i in range(0,nstations)]
  td = [feed['features'][i]['properties']['totalDocks'] for i in range(0,nstations)]
  ab = [feed['features'][i]['properties']['bikesAvailable'] for i in range(0,nstations)]
  status = [feed['features'][i]['properties']['kioskPublicStatus'] for i in range(0,nstations)]

  return zip(station_id, lat,lng,ad,td, status, station_name, ab, station_add)

def predict_demand():
  weather_rental = pd.read_csv('static/data/weather_rental.csv')
  predictors = list(weather_rental.columns)
  print(predictors)
  predictors.remove('date')
  predictors.remove('count')
  predictors.remove('is_busy')
  predictors.remove('Events')

#  train = weather_rental.sample(frac=0.666)
#  test = weather_rental.loc[~weather_rental.index.isin(train.index)]

  reg = RandomForestClassifier(n_estimators=5000, max_depth=None, min_samples_leaf=5, max_features='auto')
  reg.fit(weather_rental[predictors], weather_rental['is_busy'])

  req = Request('http://api.wunderground.com/api/1e806efcbfa974b3/geolookup/conditions/q/PA/Philadelphia.json')
  data = urlopen(req).read().decode('utf-8')
  feed = json.loads(data)

  import re
  re=re.findall(r'\d+', feed['current_observation']['relative_humidity'])
  temp=feed['current_observation']['temp_f']
  wind=feed['current_observation']['wind_mph']
  dew=feed['current_observation']['dewpoint_f']
  pressure=feed['current_observation']['pressure_in']
  visibility=feed['current_observation']['visibility_mi']
  hum=float(re[0])

  data=[[temp,hum,wind,dew,pressure,visibility]]
  pred=reg.predict(data)

  return float(pred[0])
  

"""
if __name__ == '__main__':
  port = int(os.environ.get('PORT',5000))
  app.run(host='0.0.0.0',port=port)
"""

if __name__ == '__main__':
  app.run(port=33507)
