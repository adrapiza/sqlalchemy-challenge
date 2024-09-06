# Import the dependencies.
from flask import flask
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
import datetime as dt


#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare a Base using `automap_base()`
Base = automap_base()
# Use the Base class to reflect the database tables


# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return """
    <h1>Climate App API</h1>
    <p>Available Routes:</p>
    <ul>
        <li><a href="/api/v1.0/precipitation">Precipitation Data</a></li>
        <li><a href="/api/v1.0/stations">Stations</a></li>
        <li><a href="/api/v1.0/tobs">Temperature Observations</a></li>
        <li><a href="/api/v1.0/temp/<start_date>">Temperature from Start Date</a></li>
        <li><a href="/api/v1.0/temp/<start_date>/<end_date>">Temperature between Dates</a></li>
    </ul>
    """
    
##################################################    
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Query for the last 12 months of precipitation data
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_date = most_recent_date - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_date).all()
    
    # Convert query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

###################################################
@app.route('/api/v1.0/stations')
def stations():
    # Query for station data
    results = session.query(Station.station, Station.name).all()
    
    # Convert query results to a list of dictionaries
    stations = [{"station": station, "name": name} for station, name in results]
    
    return jsonify(stations)

#######################################################
@app.route('/api/v1.0/tobs')
def tobs():
    # Find the most active station
    most_active_station_query = session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station)\
     .order_by(func.count(Measurement.station).desc())\
     .first()
     
    most_active_station_id = most_active_station_query.station
    
    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    one_year_date = most_recent_date - dt.timedelta(days=365)
    
    # Query for the last 12 months of temperature data
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id)\
        .filter(Measurement.date >= one_year_date)\
        .order_by(Measurement.date).all()
    
    # Convert query results to a list of dictionaries
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]
    
    return jsonify(tobs_data)

##########################################################
@app.route('/api/v1.0/temp/<start>')
@app.route('/api/v1.0/temp/<start>/<end>')
def temp(start, end=None):
    # Query temperature stats
    if end:
        results = session.query(
            func.min(Measurement.tobs).label('min_temp'),
            func.max(Measurement.tobs).label('max_temp'),
            func.avg(Measurement.tobs).label('avg_temp')
        ).filter(Measurement.date >= start)\
         .filter(Measurement.date <= end).one()
    else:
        results = session.query(
            func.min(Measurement.tobs).label('min_temp'),
            func.max(Measurement.tobs).label('max_temp'),
            func.avg(Measurement.tobs).label('avg_temp')
        ).filter(Measurement.date >= start).one()
    
    # Convert to a dictionary
    temp_stats = {
        "min_temp": results.min_temp,
        "max_temp": results.max_temp,
        "avg_temp": results.avg_temp
    }
    
    return jsonify(temp_stats)
############################################################
if __name__ == '__main__':
    app.run(debug=True)