from flask import Flask, render_template
from urllib.request import Request, urlopen
import json
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

@app.route('/')
def index():
  feed = get_jsonfeed()
  stations = get_stations(feed)
  startlat=39.9526
  startlng=-75.1652
  #return render_template('index.html', stations=stations, startlat=startlat, startlng=startlng)
  return render_template('home.html', stations=stations)

def get_jsonfeed():
  req = Request('https://www.rideindego.com/stations/json/', headers={'User-Agent': 'Mozilla/5.0'})
  data = urlopen(req).read().decode('utf-8')
  feed = json.loads(data)

  return feed

def get_stations(feed):
  nstations = len(feed['features'])
  station_id = [feed['features'][i]['properties']['kioskId'] for i in range(0,nstations)]
  lat = [feed['features'][i]['geometry']['coordinates'][1] for i in range(0,nstations)]
  lng = [feed['features'][i]['geometry']['coordinates'][0] for i in range(0,nstations)]
  ad = [feed['features'][i]['properties']['docksAvailable'] for i in range(0,nstations)]
  td = [feed['features'][i]['properties']['totalDocks'] for i in range(0,nstations)]

  return zip(station_id, lat,lng,ad,td)

"""
def get_jsonfeed():
  #urlData="https://api.phila.gov/bike-share-stations/v1"
  urlData="http://www.citibikenyc.com/stations/json"
  #req = urllib.request.Request("https://api.phila.gov/bike-share-stations/v1")
  #opener = urllib.request.build_opener()
  webUrl = urllib.request.urlopen(urlData)
  data = webUrl.read()
  encoding = webUrl.info().get_content_charset('utf-8')
  feed = json.loads(data.decode(encoding))
  #with urllib.request.urlopen(req) as response:
    #feed = response.read()
  return feed

def get_stations(feed):
  nstations=len(feed['features'])
  station_id = [feed['features'][i]['id'] for i in range(0,nstations)]
  lat = [feed['stationBeanList'][i]['latitude'] for i in range(0,nstations)]
  lng = [feed['stationBeanList'][i]['longitude'] for i in range(0,nstations)]
  ad = [feed['stationBeanList'][i]['availableDocks'] for i in range(0,nstations)]
  td = [feed['stationBeanList'][i]['totalDocks'] for i in range(0,nstations)]

  return zip(station_id, lat,lng,ad,td)
"""
"""
if __name__ == '__main__':
  port = int(os.environ.get('PORT',5000))
  app.run(host='0.0.0.0',port=port)
"""

if __name__ == '__main__':
  app.run(port=33507)
