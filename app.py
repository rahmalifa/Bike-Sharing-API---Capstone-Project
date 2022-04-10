from flask import Flask, request
import sqlite3
import requests
from tqdm import tqdm
import json
import numpy as np
import pandas as pd

app = Flask(__name__) 

@app.route('/')
@app.route('/home')
def home():
    return 'Hello World'

@app.route('/stations/')
def route_all_stations():
    conn = make_connection()
    stations = get_all_stations(conn)
    return stations.to_json()

@app.route('/trips/')
def route_all_trips():
    conn = make_connection()
    trips = get_all_trips(conn)
    return trips.to_json()

@app.route('/stations/<station_id>')
def route_stations_id(station_id):
    conn = make_connection()
    station = get_station_id(station_id, conn)
    return station.to_json()

@app.route('/trips/<trip_id>')
def route_trips_id(trip_id):
    conn = make_connection()
    trip = get_trip_id(trip_id, conn)
    return trip.to_json()

@app.route('/json', methods=['POST']) 
def json_example():

    req = request.get_json(force=True) # Parse the incoming json data as Dictionary

    name = req['name']
    age = req['age']
    address = req['address']

    return (f'''Hello {name}, your age is {age}, and your address in {address}
            ''')


@app.route('/stations/add', methods=['POST']) 
def route_add_station():
    # parse and transform incoming data into a tuple as we need 
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)

    conn = make_connection()
    result = insert_into_stations(data, conn)
    return result

@app.route('/trips/average_duration') 
def route_average_duration():
    conn = make_connection()
    average_duration = get_average_duration(conn)
    return average_duration.to_json()

@app.route('/trips/average_duration_bikeid/<bikeid>')
def route_average_duration_bikeid(bikeid):
    conn = make_connection()
    average_duration_bikeid = get_average_duration_bikeid(bikeid, conn)
    return average_duration_bikeid.to_json()

@app.route('/trips/avg_duration/<specified_date>')
def route_avg_duration(specified_date):
    conn = make_connection()
    avg_duration = get_avg_duration(specified_date, conn)
    return avg_duration

@app.route('/trips/duration_info/<period>/<station_id>') 
def route_duration_info(period, station_id):
    conn = make_connection()
    result = duration_info(period, station_id, conn)
    return result


############FUNCTIONS#############

def duration_info(period, station_id, conn):
    query = f"""
        SELECT 
            start_station_id, name, 
            MAX(duration_minutes) AS max_duration, 
            MIN(duration_minutes) AS min_duration,
            AVG(duration_minutes) AS avg_duration, 
            SUM(duration_minutes) AS total_duration
        FROM trips
        LEFT JOIN stations ON station_id = start_station_id
        WHERE 
            duration_minutes > 0 
            AND start_time LIKE '{period}%'
            AND station_id LIKE '{station_id}%'
        GROUP BY start_station_id
        """
    result = pd.read_sql_query(query, conn)
    return result.to_json()

def get_avg_duration(specified_date, conn):
    query = f"""SELECT *
            FROM trips 
            LEFT JOIN stations ON station_id = start_station_id WHERE start_time LIKE '{specified_date}%'"""
    selected_data = pd.read_sql_query(query, conn)
    result = selected_data.groupby(['start_station_id', 'name']).agg({
    'bikeid' : 'count', 
    'duration_minutes' : 'mean'})
    return result.to_json()


def make_connection():
    connection = sqlite3.connect('austin_bikeshare.db')
    return connection

def get_all_stations(conn):
    query = f"""SELECT * FROM stations"""
    result = pd.read_sql_query(query, conn)
    return result

def get_all_trips(conn):
    query = f"""SELECT * FROM trips LIMIT 1000"""
    result = pd.read_sql_query(query, conn)
    return result

def get_station_id(station_id, conn):
    query = f"""SELECT * FROM stations WHERE station_id = {station_id}"""
    result = pd.read_sql_query(query, conn)
    return result 

def get_trip_id(trip_id, conn):
    query = f"""SELECT * FROM trips WHERE id = {trip_id}"""
    result = pd.read_sql_query(query, conn)
    return result

def insert_into_stations(data, conn):
    query = f"""INSERT INTO stations values {data}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'

def get_average_duration(conn):
    query = f"""SELECT subscriber_type, AVG(duration_minutes) AS avg_duration_minutes FROM trips GROUP BY subscriber_type"""
    result = pd.read_sql_query(query, conn)
    return result

def get_average_duration_bikeid(bikeid,conn):
    query = f"""SELECT bikeid, AVG(duration_minutes) AS avg_duration_bike FROM trips WHERE bikeid = {bikeid} GROUP BY bikeid"""
    result = pd.read_sql_query(query, conn)
    return result

  

if __name__ == '__main__':
    app.run(debug=True, port=5000)