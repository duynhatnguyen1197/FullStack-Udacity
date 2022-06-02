#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from distutils.log import debug
import json
import sys
from urllib import response
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify 
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from sqlalchemy import true,exc
from forms import *
from models import db,Show,Venue,Artist
from sqlalchemy.exc import SQLAlchemyError
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  locals = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()
  print(places)
  for place in places:
      locals.append({
          'city': place.city,
          'state': place.state,
          'venues': [{
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': len([show for show in venue.shows if show.start_time > datetime.now()])
          } for venue in venues if
              venue.city == place.city and venue.state == place.state]
      })
  return render_template('pages/venues.html', areas=locals)


#  Search Venue
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  result = db.session.query(Venue).filter(Venue.name.ilike("%"+search_term+"%")).all()
  response={
    "count":len(result),
    "data" :[]
  }
  for venue in result:
    response["data"].append({
      "id":venue.id,
      "name":venue.name
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  response = venue.__dict__
  response["genres"]=venue.genres
  response["past_shows"]=[]
  response["upcoming_shows"]=[]
  for show in venue.shows:
    artist = Artist.query.get(show.artist_id)
    if show.start_time <= datetime.now():
        response["past_shows"].append({
        "artist_id":show.artist_id,
        "artist_name":artist.name,
        "artist_image_link":artist.image_link,
        "start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
      })
    else:
        response["upcoming_shows"].append({
        "artist_id":show.artist_id,
        "artist_name":artist.name,
        "artist_image_link":artist.image_link,
        "start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
      })
  response["past_shows_count"] = len(response["past_shows"])
  response["upcoming_shows_count"] = len(response["upcoming_shows"])
  return render_template('pages/show_venue.html', venue=response)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    form = VenueForm()
    venue = Venue(
      name = form.name.data,
      phone = form.phone.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website = form.website_link.data,
      seeking_talent = form.seeking_talent.data
    )
    if venue.seeking_talent:
      venue.seeking_description = form.seeking_description.data
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    print(error)
    db.session.rollback()
    flash('An error occurred. Venue  could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  try:
    venue =  Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    db.session.close()
    return jsonify({ 'success': True })
  except:
    db.session.rollback()
    db.session.close()
    return jsonify({'success':False})


#  Update Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.phone = form.phone.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website = form.website_link.data,
    venue.seeking_talent = form.seeking_talent.data
    if venue.seeking_talent:
      venue.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    print(error)
    db.session.rollback()
    flash('An error occurred. Venue  could not be edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  response = []
  artists = Artist.query.all()
  for artist in artists:
    response.append({
      "id":artist.id,
      "name":artist.name
    })
  return render_template('pages/artists.html', artists=response)


#  Search Artist
#  ----------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form['search_term']
  result = db.session.query(Artist).filter(Artist.name.ilike("%"+search_term+"%")).all()
  response={
    "count":len(result),
    "data" :[]
  }
  for artist in result:
    response["data"].append({
      "id":artist.id,
      "name":artist.name
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  response = artist.__dict__
  response["genres"]=artist.genres
  response["past_shows"]=[]
  response["upcoming_shows"]=[]
  for show in artist.shows:
    print(show.start_time)
    venue = Venue.query.get(show.venue_id)
    if show.start_time <= datetime.now():
        response["past_shows"].append({
        "venue_id":show.venue_id,
        "venue_name":venue.name,
        "venue_image_link":venue.image_link,
        "start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
      })
    else:
        response["upcoming_shows"].append({
        "venue_id":show.venue_id,
        "venue_name":venue.name,
        "venue_image_link":venue.image_link,
        "start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
      })
  response["past_shows_count"] = len(response["past_shows"])
  response["upcoming_shows_count"] = len(response["upcoming_shows"])
  return render_template('pages/show_artist.html', artist=response)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form = ArtistForm()
    artist = Artist(
      name = form.name.data,
      phone = form.phone.data,
      city = form.city.data,
      state = form.state.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website = form.website_link.data,
      seeking_venue = form.seeking_venue.data
    )
    if artist.seeking_venue:
      artist.seeking_description = form.seeking_description.data
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    print(error)
    db.session.rollback()
    flash('An error occurred. Artist  could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Update Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.phone = form.phone.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.genres = form.genres.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website = form.website_link.data,
    artist.seeking_venue = form.seeking_venue.data
    if artist.seeking_venue:
      artist.seeking_description = form.seeking_description.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    print(error)
    db.session.rollback()
    flash('An error occurred. Artist  could not be edited.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  response = []
  for show in shows:
    venue = Venue.query.filter(Venue.id == show.venue_id).first()
    artist = Artist.query.filter(Artist.id == show.artist_id).first()
    response.append({
      "venue_id":venue.id,
      "venue_name":venue.name,
      "artist_id":artist.id,
      "artist_name":artist.name,
      "artist_image_link":artist.image_link,
      "start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })
  return render_template('pages/shows.html', shows=response)


#  Create Show
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    form = ShowForm()
    show = Show(
      artist_id=form.artist_id.data,
      venue_id=form.venue_id.data,
      start_time=form.start_time.data
    )
    # show.start_time = datetime.strptime(''.join(reqData.get("start_time")),"%Y-%m-%d %H:%M:%S")
    db.session.add(show)
    db.session.commit()
    flash('Show ' + str(show.id) + '  was successfully listed!')
  except SQLAlchemyError as e:
    print(e)
    db.session.rollback()
    flash('An error occurred. Show ' + str(show.id) + '  could not be edited.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
