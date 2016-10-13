# # Loading, cleaning, and merging datasets

# In[1]:

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


# In[24]:

rentals1 = pd.read_csv('Indego_Trips_2015Q4.csv')
#print(rentals1.head(5))
rentals2 = pd.read_csv('Indego_Trips_2016Q1.csv')
#print(rentals2.head(5))
rentals3 = pd.read_csv('Indego_Trips_2016Q2.csv')
#print(rentals3.head(5))

rentals1['start_time'] = rentals1['start_time'].str.replace(r'\d+\s', '2015 ')
rentals1['end_time'] = rentals1['end_time'].str.replace(r'\d+\s', '2015 ')
print(rentals1.head(10))
rentals = rentals1.append(rentals2).append(rentals3)
rentals.tail(5)


# In[3]:

rentals.head(5)


# In[4]:

rentals.columns


# In[5]:

stime = '(?P<hour>\d+):(?P<minute>\d+)'
stimes = rentals['start_time'].str.extract(stime, expand=True)
stimes.head(5)
etime = '(?P<hour>\d+):(?P<minute>\d+)'
etimes = rentals['end_time'].str.extract(etime, expand=True)
etimes.head(5)
rentals['start_hour']=stimes['hour'].astype(float)
rentals['end_hour']=etimes['hour'].astype(float)
rentals['count']=1

date = '(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)'
dates = rentals['start_time'].str.extract(date, expand=True)
print(dates.dtypes)
rentals['date']=dates['year'].astype(str)+'-'+dates['month'].astype(str)+'-'+dates['day'].astype(str)


# In[16]:

print(rentals.shape[0])
rentals.head(5)
rentals.tail(5)


# In[13]:

rentals_countt = rentals.groupby('date', as_index=False).sum()
rentals_count = rentals_countt[['date','count']]
rentals_count.head(20)
print(rentals_count.shape[0])
sns.plt.hist(rentals_count['count'])
# Total number of docks is 1995
print(rentals_count['count'].describe())


# In[8]:

from urllib.request import Request, urlopen
import json
req = Request('https://www.rideindego.com/stations/json/', headers={'User-Agent': 'Mozilla/5.0'})
data = urlopen(req).read().decode('utf-8')
feed = json.loads(data)
nstations = len(feed['features'])
td = [feed['features'][i]['properties']['totalDocks'] for i in range(0,nstations)]
station_id = [feed['features'][i]['properties']['kioskId'] for i in range(0,nstations)]
print(td, station_id)
station_info=pd.DataFrame({'station': station_id, 'total_docks':td})
print(station_info.head(5))
print(station_info['total_docks'].sum())


# In order to predict station popularity by hour, we want to make a new df with stations, hours, and counts of rentals at those hours.

# In[9]:

weather=pd.read_csv('Weather_Oct_Jun.csv')
print(weather.columns)
weather.tail(5)


# ## With the two data frames, merge them based on date

# In[33]:

# do the same for the weather
weather_day = weather[['EDT','Mean TemperatureF',' Mean Humidity',' Mean Wind SpeedMPH','MeanDew PointF',                       ' Mean Sea Level PressureIn',' Mean VisibilityMiles',' Events']]
weather_day.columns = ['date','mean temp','mean hum','mean wind','mean dew','mean pressure',                      'mean visib','Events']

# merge based on date
weather_rental = pd.merge(rentals_count, weather_day, how='left', on='date')
weather_rental.fillna('None', inplace=True)
weather_rental.tail(20)


# ## Now calculate classifier for bike demand low = 0, or fair = 1, busy = 2, very busy = 3

# In[34]:

stats=rentals_count['count'].describe()

def is_busy(row):
    stats=rentals_count['count'].describe()
    #if bikes parked at that station at that hour is greater, we know station is mostly full (so not busy)
    if row['count'] <= stats['25%']:
        return 0
    elif row['count'] > stats['25%'] and row['count'] <= stats['50%']:
        return 1
    elif row['count'] > stats['50%'] and row['count'] <= stats['75%']:
        return 2
    else:
        return 3
        
weather_rental['is_busy'] = weather_rental.apply(is_busy, axis=1)
weather_rental.head(5)

weather_rental.to_csv('weather_rental.csv', index=False)

"""
# ### Now we have a clean dataframe with the date, weather info, hour, and bike rental counts

# # Time to train and predict

# In[35]:

train = weather_rental.sample(frac=.8)
test = weather_rental.loc[~weather_rental.index.isin(train.index)]
test.head(3)


# In[36]:

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error

predictors = list(weather_rental.columns)
predictors.remove('date')
predictors.remove('count')
predictors.remove('is_busy')
predictors.remove('Events')

reg = RandomForestClassifier(n_estimators=10, max_depth=None,                             min_samples_split=10, min_samples_leaf=5, max_features='auto')
reg.fit(train[predictors], train['is_busy'])

pred = reg.predict(test[predictors])
mse = mean_squared_error(test['is_busy'],pred)
print(mse)

print (pred[:15])
print (test['is_busy'].iloc[:15])
test.head(15)


# # Pull weather data for today and predict for this hour

# In[41]:

req = Request('http://api.wunderground.com/api/1e806efcbfa974b3/geolookup/conditions/q/PA/Philadelphia.json')
data = urlopen(req).read().decode('utf-8')
feed = json.loads(data)

print (feed['location']['city'])
print (feed['current_observation']['temp_f'])
print (feed['current_observation']['wind_mph'])
print (feed['current_observation']['relative_humidity'])


#weather_day.columns = ['date','mean temp','mean hum','mean wind','mean dew','mean pressure',\
                      #'mean visib']
print(predictors)

import re
re=re.findall(r'\d+', feed['current_observation']['relative_humidity'])
temp=feed['current_observation']['temp_f']
wind=feed['current_observation']['wind_mph']
dew=feed['current_observation']['dewpoint_f']
pressure=feed['current_observation']['pressure_in']
visibility=feed['current_observation']['visibility_mi']
hum=float(re[0])
hour=20.0

data=[[temp,hum,wind,dew,pressure,visibility]]
#today = pd.DataFrame(data,columns=predictors)

#print(today)
reg.predict(data)
"""
