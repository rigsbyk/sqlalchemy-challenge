import numpy as np
import datetime as dt

import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station 

session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def Home():
    return (
        f"Welcome to the Home Page!<br/>"
        f"<br/>"
        f"All Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"Put the start date in 'YYYY-MM-DD' format<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Put the start and date in 'YYYY-MM-DD' format<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    last_yr = session.query(Measurement.date,Measurement.prcp).\
        order_by(Measurement.date.desc()).first()
    
    last_date = last_yr[0]

    last_year = dt.datetime.strptime(last_date,"%Y-%m-%d") - (dt.timedelta(days=365))
    year_ago = last_year.strftime("%Y-%m-%d")

    prcp_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).order_by(Measurement.date).all()

    prcp_list = []
    for p in prcp_results:
        pdict = {"Date":p[0],"Prcp":p[1]}
        prcp_list.append(pdict)
    return jsonify(prcp_list)

@app.route("/api/v1.0/stations")
def stations():
    station_results = session.query(Station.station,Station.name).all()

    station_list = []
    for stations in station_results:
        sdict = {"Station":stations[0],"Station Name":stations[1]}
        station_list.append(sdict)
    return jsonify(station_list) 

@app.route("/api/v1.0/tobs")
def tobs():

    # Grabbing the latest date entry
    last_12 = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date.desc()).first()

    # Get the first item(date) out of the tuple so it is just the date
    last_date = last_12[0]

    # Calculate the date 1 year ago from the last data point in the database
    last_year = dt.datetime.strptime(last_date,"%Y-%m-%d") - (dt.timedelta(days=365))
    # Reformatting date to ("%Y-%m-%d")
    year_ago = last_year.strftime("%Y-%m-%d")

    # Choose the station with the highest number of temperature observations.
    highest_obsv = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).\
    order_by(func.count(Measurement.tobs).desc()).first()
    highest_obsv_data = highest_obsv[0]

    # Query the last 12 months of temperature observation data for this station
    last_yr_observation = session.query(Measurement.date,Measurement.tobs).\
    filter(Measurement.date >= year_ago).filter(Measurement.station == highest_obsv_data).all()

    tobs_list=[]
    for tobs in last_yr_observation:
        tdict = {"Date":tobs[0],"Tobs":tobs[1]}
        tobs_list.append(tdict)

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
def start_date(start):

    startdt = session.query(Measurement.date,func.avg(Measurement.tobs),func.min(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).group_by(Measurement.date).all()

    start_dt_list = []
    for stdt in startdt:
       stdict = {"Date":stdt[0],"Avg.Temp":stdt[1],"Min Temp":stdt[2],"Max Temp":stdt[3]}
       start_dt_list.append(stdict)
    return jsonify(start_dt_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    date_range = session.query(Measurement.date,func.avg(Measurement.tobs),func.min(Measurement.tobs),func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    date_range_list = []
    for dt_rng in date_range:
        dt_rng_dict = {"Date":dt_rng[0],"Avg.Temp":dt_rng[1],"Min Temp":dt_rng[2],"Max Temp":dt_rng[3]}
        date_range_list.append(dt_rng_dict)
    return jsonify(date_range_list)


if __name__ == "__main__":
    app.run(debug=True)