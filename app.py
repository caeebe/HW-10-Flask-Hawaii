import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from datetime import datetime


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#####################
# Useful functions  #
#####################

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy-mm-dd<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def rain():
    """Return a list of dates and precipitation"""
    # Query all dates and rain
    results1 = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and append to a list of all_rain
    all_rain = []
    for date, precip, in results1:
        rain_dict = {}
        rain_dict["date"] = date
        rain_dict["prcp"] = precip
        all_rain.append(rain_dict)

    return jsonify(all_rain)


@app.route("/api/v1.0/stations")
def station_names():
    """Return a list of station names"""
    # Query all station names
    results2 = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results2))

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperature():
    """Return a list of dates and temperature for the last year of data"""
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_dt = datetime.strptime(last_date[0], '%Y-%m-%d')
    year_ago = last_dt - dt.timedelta(days=366)

    # Query the year of temps
    results3 = session.query(Measurement.date, Measurement.tobs).\
       filter(Measurement.date > year_ago.strftime("%Y-%m-%d")).order_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list
    year_temp = []
    for date, tobs, in results3:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        year_temp.append(temp_dict)

    return jsonify(year_temp)


@app.route("/api/v1.0/<start>")
def start_temp(start):
    """returns the min, avg, and max temperatures from a start date to the present"""
    """ start must be in the format YYYY-MM-DD """

    # Query the latest date in the data
    end = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Query the temperature min, avg, and max temperatures 
    mam_temps = calc_temps(start, end[0])

    start_dict = {}
    start_dict["min"] = mam_temps[0][0]
    start_dict["avg"] = mam_temps[0][1]
    start_dict["max"] = mam_temps[0][2]

    return jsonify(start_dict)


@app.route("/api/v1.0/<start>/<end>")
def range_temp(start,end):
    """returns the min, avg, and max temperatures from a start date to the present"""
    """ start must be in the format YYYY-MM-DD """

    # Query the temperature min, avg, and max temperatures 
    mam__range_temps = calc_temps(start, end)

    # Create a dictionary from the row data and append to a list of all_passengers
    range_dict = {}
    range_dict["min"] = mam__range_temps[0][0]
    range_dict["avg"] = mam__range_temps[0][1]
    range_dict["max"] = mam__range_temps[0][2]

    return jsonify(range_dict)


if __name__ == '__main__':
    app.run(debug=True)
