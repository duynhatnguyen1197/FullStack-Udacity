#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
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
from flask_wtf import Form
from sqlalchemy import true
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    genres = db.relationship('Genre_Venue',cascade="all,delete",backref='venue',lazy=True)
    shows = db.relationship('Show',cascade="all,delete",backref='venue',lazy=True)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(300))
    genres = db.relationship('Genre_Artist',cascade="all,delete",backref='artist',lazy=True)
    shows = db.relationship('Show',cascade="all,delete",backref='artist',lazy=True)

class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class Genre_Venue(db.Model):
  __tablename__ = 'Genre_Venue'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
  genre_id = db.Column(db.Integer,db.ForeignKey('Genre.id'),nullable=False)

class Genre_Artist(db.Model):
  __tablename__ = 'Genre_Artist'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
  genre_id = db.Column(db.Integer,db.ForeignKey('Genre.id'),nullable=False)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
    start_time = db.Column(db.DateTime())

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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

#TODO: insert dummy data to run project
@app.route('/generate-data')
def generate_data():
  try:
    genre = Genre.query.first()
    if not bool(genre): #if DB empty then insert new data or else it will skip insert
      genres = []
      genres.append(Genre(name='Jazz'))
      genres.append(Genre(name='Reggae'))
      genres.append(Genre(name='Swing'))
      genres.append(Genre(name='Classical'))
      genres.append(Genre(name='Folk'))
      genres.append(Genre(name='R&B'))
      genres.append(Genre(name='Hip-Hop'))
      genres.append(Genre(name='Rock n Roll'))
      genres.append(Genre(name='Alternative'))
      genres.append(Genre(name='Blues'))
      genres.append(Genre(name='Country'))
      genres.append(Genre(name='Electronic'))
      genres.append(Genre(name='Funk'))
      genres.append(Genre(name='Heavy Metal'))
      genres.append(Genre(name='Instrumental'))
      genres.append(Genre(name='Musical Theatre'))
      genres.append(Genre(name='Pop'))
      genres.append(Genre(name='Funk'))
      genres.append(Genre(name='Punk'))
      genres.append(Genre(name='Soul'))
      genres.append(Genre(name='Other'))
      db.session.add_all(genres)
      db.session.commit()
      venues=[{
        "name": "The Musical Hop",
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
      },{
        "name": "The Dueling Pianos Bar",
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80"
      },{
        "name": "Park Square Live Music & Coffee",
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80"
      }]
      listVenues = []
      for venue in venues:
        venue = json.dumps(venue)
        x = json.loads(venue, object_hook=lambda d: Venue(**d))
        listVenues.append(x)
      db.session.add_all(listVenues)
      db.session.commit()

      artists=[{
        "name": "Guns N Petals",
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
      },{
        "name": "Matt Quevedo",
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80"
      },{
        "name": "The Wild Sax Band",
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80"
      }]
      listArtists = []
      for artist in artists:
        artist = json.dumps(artist)
        x = json.loads(artist, object_hook=lambda d: Artist(**d))
        listArtists.append(x)
      db.session.add_all(listArtists)
      db.session.commit()

      shows=[{
        "venue_id": 1,
        "artist_id": 1,
        "start_time": "2019-05-21T21:30:00.000Z"
      }, {
        "venue_id": 3,
        "artist_id": 2,
        "start_time": "2019-06-15T23:00:00.000Z"
      }, {
        "venue_id": 3,
        "artist_id": 3,
        "start_time": "2035-04-01T20:00:00.000Z"
      }, {
        "venue_id": 3,
        "artist_id": 3,
        "start_time": "2035-04-08T20:00:00.000Z"
      }, {
        "venue_id": 3,
        "artist_id": 3,
        "start_time": "2035-04-15T20:00:00.000Z"
      }]
      listShows = []
      for show in shows:
        show = json.dumps(show)
        x = json.loads(show, object_hook=lambda d: Show(**d))
        listShows.append(x)
      db.session.add_all(listShows)
      db.session.commit()

      genre_venues = [{
        "venue_id":1,
        "genre_id":1
      },{
        "venue_id":1,
        "genre_id":2
      },{
        "venue_id":1,
        "genre_id":3
      },{
        "venue_id":1,
        "genre_id":4
      },{
        "venue_id":1,
        "genre_id":5
      },{
        "venue_id":2,
        "genre_id":4
      },{
        "venue_id":2,
        "genre_id":7
      },{
        "venue_id":2,
        "genre_id":8
      },{
        "venue_id":3,
        "genre_id":1
      },{
        "venue_id":3,
        "genre_id":5
      },{
        "venue_id":3,
        "genre_id":6
      },{
        "venue_id":3,
        "genre_id":9
      }]
      listGenreVenues = []
      for i in genre_venues:
        i = json.dumps(i)
        x = json.loads(i, object_hook=lambda d: Genre_Venue(**d))
        listGenreVenues.append(x)

      db.session.add_all(listGenreVenues)
      db.session.commit()

      genre_artists = [{
        "artist_id":1,
        "genre_id":9
      },{
        "artist_id":2,
        "genre_id":1
      },{
        "artist_id":3,
        "genre_id":1
      },{
        "artist_id":3,
        "genre_id":4
      }]
      listGenreArtists = []
      for i in genre_artists:
        i = json.dumps(i)
        x = json.loads(i, object_hook=lambda d: Genre_Artist(**d))
        listGenreArtists.append(x)
      db.session.add_all(listGenreArtists)
      db.session.commit()
      return 'success'
    else:
      return 'DB is not empty '
  except:
    db.session.rollback()
    return 'error import new data'
  


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  venues = Venue.query.all()
  seen = set()
  regions = []
  for venue in venues:
    t = tuple(venue.city)
    if t not in seen:
      seen.add(t)
      regions.append({'city':venue.city,'state':venue.state})
  for r in regions:
    r['venues']=[]
    for v in venues:
      if v.city == r['city']:
        r['venues'].append({
          "id":v.id,
          "name":v.name
        })
  return render_template('pages/venues.html', areas=regions)

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

def checkPastOrFutureShow(shows):
  result={"past_shows":[],"upcoming_shows":[]} 
  today = datetime.now()
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    if today > show.start_time:
      result["past_shows"].append({
        "artist_id":show.artist_id,
        "artist_name":artist.name,
        "artist_image_link":artist.image_link,
        "start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
      })
    else:
      result["upcoming_shows"].append({
        "artist_id":show.artist_id,
        "artist_name":artist.name,
        "artist_image_link":artist.image_link,
        "start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
      })
  return result


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  genresId = Genre_Venue.query.filter(Genre_Venue.venue_id == venue_id).all()
  shows = Show.query.filter(Show.venue_id == venue_id).all()
  respGenreList = []
  for i in genresId:
    genre = Genre.query.get(i.genre_id)
    respGenreList.append(genre.name)
  
  respShow = checkPastOrFutureShow(shows)
  response = venue.__dict__
  response["genres"]=respGenreList
  response["past_shows"] = respShow["past_shows"]
  response["upcoming_shows"] = respShow["upcoming_shows"]
  response["past_shows_count"] = len(respShow["past_shows"])
  response["upcoming_shows_count"] = len(respShow["upcoming_shows"])

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
    seekingTalent = False
    reqData =request.form.to_dict(flat=False)
    if reqData.get("seeking_talent") =='y':
      seekingTalent = True 
    venue = Venue()
    venue.name = ''.join(reqData["name"])
    venue.phone=''.join(reqData["phone"])
    venue.city = ''.join(reqData["city"])
    venue.state = ''.join(reqData["state"])
    venue.address = ''.join(reqData["address"])
    venue.facebook_link = ''.join(reqData["facebook_link"])
    venue.image_link = ''.join(reqData["image_link"])
    venue.website = ''.join(reqData["website_link"])
    venue.seeking_talent = seekingTalent
    venue.seeking_description = ''.join(reqData["seeking_description"])
    db.session.add(venue)
    db.session.flush()
    genres = reqData["genres"]
    for i in genres:
      genre = Genre.query.filter(Genre.name==i).first()
      genreVenue = Genre_Venue(venue_id=venue.id,genre_id = genre.id)
      db.session.add(genreVenue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue =  Venue.query.get(venue_id)
    print(venue.name)
    venueName = venue.name
    db.session.delete(venue)
    db.session.commit()
    print(venue)
    db.session.close()
    return jsonify({ 'success': True })
  except:
    db.session.rollback()
    db.session.close()
    return jsonify({'success':False})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  response = []
  artists = Artist.query.all()
  for artist in artists:
    response.append({
      "id":artist.id,
      "name":artist.name
    })
  return render_template('pages/artists.html', artists=response)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
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
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  genresId = Genre_Artist.query.filter(Genre_Artist.artist_id == artist_id).all()
  shows = Show.query.filter(Show.venue_id == artist_id).all()
  respGenreList = []
  for i in genresId:
    genre = Genre.query.get(i.genre_id)
    respGenreList.append(genre.name)
  respShow = checkPastOrFutureShow(shows)
  response = artist.__dict__
  response["genres"]=respGenreList
  response["past_shows"] = respShow["past_shows"]
  response["upcoming_shows"] = respShow["upcoming_shows"]
  response["past_shows_count"] = len(respShow["past_shows"])
  response["upcoming_shows_count"] = len(respShow["upcoming_shows"])

  return render_template('pages/show_artist.html', artist=response)

#  Update
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
    seekingVenue = False
    reqData =request.form.to_dict(flat=False)
    if reqData.get("seeking_venue")[0] =='y':
      seekingVenue = True 
    artist = Artist.query.get(artist_id)
    artist.name = ''.join(reqData["name"])
    artist.phone=''.join(reqData["phone"])
    artist.city = ''.join(reqData["city"])
    artist.state = ''.join(reqData["state"])
    artist.facebook_link = ''.join(reqData["facebook_link"])
    artist.image_link = ''.join(reqData["image_link"])
    artist.website = ''.join(reqData["website_link"])
    artist.seeking_venue = seekingVenue
    artist.seeking_description = ''.join(reqData["seeking_description"])
    db.session.commit()
    oldGenreArtist = Genre_Artist.__table__.delete().where(Genre_Artist.artist_id == artist.id)
    db.session.execute(oldGenreArtist)
    db.session.commit()
    genres = reqData["genres"]
    listGenres = []
    for i in genres:
      genre = Genre.query.filter(Genre.name==i).first()
      newGenreArtist = Genre_Artist(artist_id=artist.id,genre_id = genre.id)
      listGenres.append(newGenreArtist)
    db.session.add_all(listGenres)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    seekingTalent = False
    reqData =request.form.to_dict(flat=False)
    if reqData.get("seeking_talent")[0] =='y':
      seekingTalent = True 
    venue = Venue.query.get(venue_id)
    venue.name = ''.join(reqData["name"])
    venue.phone=''.join(reqData["phone"])
    venue.city = ''.join(reqData["city"])
    venue.state = ''.join(reqData["state"])
    venue.address = ''.join(reqData["address"])
    venue.facebook_link = ''.join(reqData["facebook_link"])
    venue.image_link = ''.join(reqData["image_link"])
    venue.website = ''.join(reqData["website_link"])
    venue.seeking_talent = seekingTalent
    venue.seeking_description = ''.join(reqData["seeking_description"])
    db.session.commit()
    oldGenreArtist = Genre_Venue.__table__.delete().where(Genre_Venue.venue_id == venue.id)
    db.session.execute(oldGenreArtist)
    db.session.commit()
    genres = reqData["genres"]
    listVenues = []
    for i in genres:
      genre = Genre.query.filter(Genre.name==i).first()
      newGenreArtist = Genre_Venue(venue_id=venue.id,genre_id = genre.id)
      listVenues.append(newGenreArtist)
    db.session.add_all(listVenues)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    seekingVenue = False
    reqData =request.form.to_dict(flat=False)
    if reqData.get("seeking_venue") =='y':
      seekingTalent = True 
    artist = Artist()
    artist.name = ''.join(reqData["name"])
    artist.phone=''.join(reqData["phone"])
    artist.city = ''.join(reqData["city"])
    artist.state = ''.join(reqData["state"])
    artist.facebook_link = ''.join(reqData["facebook_link"])
    artist.image_link = ''.join(reqData["image_link"])
    artist.website = ''.join(reqData["website_link"])
    artist.seeking_venue = seekingVenue
    artist.seeking_description = ''.join(reqData["seeking_description"])
    db.session.add(artist)
    for attr, value in artist.__dict__.items():
        print(attr, value)
    db.session.flush()
    genres = reqData["genres"]
    for i in genres:
      genre = Genre.query.filter(Genre.name==i).first()
      genreVenue = Genre_Artist(artist_id=artist.id,genre_id = genre.id)
      db.session.add(genreVenue)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
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

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    reqData =request.form.to_dict(flat=False)
    show = Show()
    show.artist_id = ''.join(reqData["artist_id"])
    show.venue_id=''.join(reqData["venue_id"])
    show.start_time = datetime.strptime(''.join(reqData.get("start_time")),"%Y-%m-%d %H:%M:%S")
    db.session.add(show)
    db.session.commit()
    flash('Show ' + str(show.id) + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show ' + str(show.id) + ' could not be listed.')
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
