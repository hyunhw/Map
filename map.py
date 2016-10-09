from flask import Flask, render_template
from urllib.request import Request, urlopen
import json
import pandas as pd
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
  feed = get_jsonfeed()
  stations = get_stations(feed)
  startlat=39.9526
  startlng=-75.1652
  return render_template('home.html', stations=stations)

@app.route('/about')
def about():
  return render_template('about.html')

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

"""
if __name__ == '__main__':
  port = int(os.environ.get('PORT',5000))
  app.run(host='0.0.0.0',port=port)
"""

if __name__ == '__main__':
  app.run(port=33507)
