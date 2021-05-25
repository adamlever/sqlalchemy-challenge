# Import Dependencies
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Flask Setup
app = Flask(__name__)


# Database Setup - create engine, reflect database and tables
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Routes
@app.route("/")
def home():
    print("Server received request for 'Home' page")
    return (
        f"Welcome to the SQL Alchemy Challenge API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )


# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of precipitation data from the last year of data as json"""
    session = Session(engine)
    
    sel = [Measurement.date, Measurement.prcp]
    precipitation_data = session.query(*sel).filter(Measurement.date >= '2016-08-23').all()
    
    session.close()

    precipitation_list = []
    for date, prcp in precipitation_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation_list.append(prcp_dict)

    return jsonify(precipitation_list)


# Station route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations as json"""
    session = Session(engine)
    
    stations = session.query(Station.station, Station.name).order_by(Station.station).all()
    
    session.close()

    return jsonify(stations)


# Tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    """Dates and temperature observations of the most active station for the last year of data as json"""
    session = Session(engine)

    most_active = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]
    sel = [Measurement.date, Measurement.tobs]
    temperature_observations = session.query(*sel).filter(Measurement.station == most_active).filter(Measurement.date >= '2016-08-23').all()

    session.close()

    temperature_list = []
    for date, tobs in temperature_observations:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        temperature_list.append(tobs_dict)

    return jsonify(temperature_list)


# Start route
@app.route("/api/v1.0/<start>")
def start(start):
    """Return the minimum temperature, the average temperature, and the max temperature for a given start date as json"""
    session = Session(engine)

    start_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    start_list = []
    for min, avg, max in start_query:
        start_dict = {}
        start_dict["min_temp"] = min
        start_dict["avg_temp"] = avg
        start_dict["max_temp"] = max
        start_list.append(start_dict)

    return jsonify(start_list)


# Start/end route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    """Return the minimum temperature, the average temperature, and the max temperature for a given start-end date range as json"""
    session = Session(engine)

    start_end_query = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    start_end_list = []
    for min, avg, max in start_end_query:
        start_end_dict = {}
        start_end_dict["min_temp"] = min
        start_end_dict["avg_temp"] = avg
        start_end_dict["max_temp"] = max
        start_end_list.append(start_end_dict)

    return jsonify(start_end_list)


# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
