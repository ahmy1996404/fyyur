#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from datetime import datetime
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app , db)


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
    # array column for genres of venue
    genres = db.Column(db.ARRAY(db.String))
    show = db.relationship('Show', backref='venue' , lazy=True)
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    show = db.relationship('Show', backref='artist' , lazy=True)
    seeking_venue = db.Column(db.Boolean)
    seeking_description =  db.Column(db.String(120))

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime)
    # foreign key to venue table
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id') , nullable=False )
    # foreign key to artist table
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id') , nullable=False )


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
 # i used strftime("%A %b %d %Y, %I:%M%p")  to filter date becuse when i use  format_datetime there error 'NoneType' object has no attribute 'days'
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  data=[]
  # to get time now to use it in upcomming show
  dateNow=datetime.now()
  # get venues
  venues = Venue.query.all()
  # make set that doesn't repeate or dublicate the values
  citiesSet= set()
  for venue in venues:
    # fill the set with venues cities and states
    citiesSet.add((venue.city, venue.state))
  # get the venues for every city and state
  for citystate in citiesSet:
      ven=[]
      # get venues that thair city matches with the city
      listVenues =  Venue.query.filter_by(city = citystate[0], state = citystate[1]).all()
      for list in listVenues:
          # get the shows for this venue
          venue_show = Show.query.filter_by(venue_id = list.id)
          # init the no of show to make it 0 at new venue at for
          numOfShows=0
          for show in venue_show:
            # check the next shows
            if (show.start_date > dateNow):
              numOfShows+=1

        # ven contain the id and name of the venues that matches with the city
          ven.append({
            "id":list.id,
            "name":list.name,
            "num_upcoming_shows":numOfShows
          })
      # make data  apper like :- data=[{"city": "San Francisco","state": "CA","venues": [{"id": 1,"name": "The Musical Hop","num_upcoming_shows": 0,},
      data.append({
        "city":citystate[0],
        "state": citystate[1],
        "venues":ven

      })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  key = request.form.get('search_term')
  list=[]
  dateNow=datetime.now()
  filteredVenues = Venue.query.filter(Venue.name.like('%'+ key + '%')).all()
  for venue in filteredVenues:
    venue_show = Show.query.filter_by(venue_id=venue.id)
    num_upcoming = 0
    for show in venue_show:
      # check the next shows
      if (show.start_date > dateNow):
        num_upcoming += 1

    list.append({
      "id": venue.id,
      "name":venue.name,
      "num_upcoming_shows":num_upcoming
    })
  response={
    "count":len(filteredVenues),
    "data":list

  }
  print(response)

  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  past_shows=[]
  upcoming_shows=[]
  past_shows_count=0
  upcoming_shows_count=0
  dateNow = datetime.now()
  for v_show in venue.show:
    if v_show.start_date > dateNow:
      upcoming_shows_count+=1
      upcoming_shows.append({
        'artist_id': v_show.artist_id,
        'artist_name': v_show.artist.name,
        'artist_image_link': v_show.artist.image_link,
        'start_time': v_show.start_date.strftime("%A %b %d %Y, %I:%M%p")
      })
    elif v_show.start_date < dateNow:
      past_shows_count += 1
      past_shows.append({
        'artist_id': v_show.artist_id,
        'artist_name': v_show.artist.name,
        'artist_image_link': v_show.artist.image_link,
        'start_time': v_show.start_date.strftime("%A %b %d %Y, %I:%M%p")
      })


  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":past_shows ,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  print(data)
  # shows the venue page with the given venue_id
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error= False
  try:
        #insert form data as a new Venue record in the db, instead
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']
        genres = request.form.getlist('genres')
        if (request.form['seeking_talent'] =='True'):
          seeking_talent = True
        else:
          seeking_talent = False
        seeking_description = request.form['seeking_description']
        image_link = request.form['image_link']
        website = request.form['website']
        # modify data to be the data object returned from db insertion
        venue = Venue(name=name, city=city, state=state ,address=address, phone=phone, facebook_link=facebook_link , genres=genres, seeking_talent= seeking_talent , seeking_description=seeking_description ,image_link=image_link , website=website)
        db.session.add(venue)
        db.session.commit()

  except():
        db.session.rollback()
        error = True
  finally:
        db.session.close()
      # if there error
  if error:
        flash('Venue ' + request.form['name'] + ' not listed!')
        abort(500)
  else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except():
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  if error:
      abort(500)
  else:
      flash('Venue  was deleted successfully')
      return jsonify({'success': True})

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = Artist.query.all()
  for artist in artists:
        data.append({
            "id":artist.id,
            "name":artist.name
           })
  print(data)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
   # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  key = request.form.get('search_term')
  list = []
  dateNow = datetime.now()
  filteredArtists = Artist.query.filter(Artist.name.like('%' + key + '%')).all()
  for artist in filteredArtists:
      artist_show = Show.query.filter_by(artist_id=artist.id)
      num_upcoming = 0
      for show in artist_show:
          # check the next shows
          if (show.start_date > dateNow):
              num_upcoming += 1

      list.append({
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": num_upcoming
      })
  response = {
      "count": len(filteredArtists),
      "data": list

  }
  print(response)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if not artist :
      return render_template('errors/404.html')
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0
  dateNow = datetime.now()
  for a_show in artist.show:
      if a_show.start_date > dateNow:
          upcoming_shows_count += 1
          upcoming_shows.append({
              'venue_id': a_show.venue_id,
              'venue_name': a_show.venue.name,
              'venue_image_link': a_show.venue.image_link,
              'start_time': a_show.start_date.strftime("%A %b %d %Y, %I:%M%p")
          })
      elif a_show.start_date < dateNow:
          past_shows_count += 1
          past_shows.append({
              'venue_id': a_show.venue_id,
              'venue_name': a_show.venue.name,
              'venue_image_link': a_show.venue.image_link,
              'start_time': a_show.start_date.strftime("%A %b %d %Y, %I:%M%p")
          })

  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": past_shows_count,
      "upcoming_shows_count": upcoming_shows_count,
  }
  print(data)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  art = Artist.query.get(artist_id)
  if not art:
      return render_template('errors/404.html')
  else:
      artist={
        "id": art.id,
        "name": art.name,
        "genres": art.genres,
        "city": art.city,
        "state": art.state,
        "phone": art.phone,
        "website": art.website,
        "facebook_link": art.facebook_link,
        "seeking_venue": art.seeking_venue,
        "seeking_description": art.seeking_description,
        "image_link": art.image_link
      }
      return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
      name = request.form['name']
      city = request.form['city']
      state = request.form['state']
      phone = request.form['phone']
      facebook_link = request.form['facebook_link']
      genres = request.form.getlist('genres')
      if (request.form['seeking_venue'] == 'True'):
          seeking_venue = True
      else:
          seeking_venue = False
      seeking_description = request.form['seeking_description']
      image_link = request.form['image_link']
      website = request.form['website']

      artist = Artist.query.get(artist_id)

      artist.name = name
      artist.city = city
      artist.state = state
      artist.phone = phone
      artist.facebook_link = facebook_link
      artist.genres = genres
      artist.seeking_venue = seeking_venue
      artist.seeking_description = seeking_description
      artist.image_link = image_link
      artist.website = website
      db.session.commit()

  except():
      db.session.rollback()
      error = True
  finally:
      db.session.close()
  # if there error
  if error:
      flash('Artist ' + request.form['name'] + ' not listed!')
      abort(500)
  else:
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  ven = Venue.query.get(venue_id)
  if not ven:
      return render_template('errors/404.html')
  venue={
    "id": ven.id,
    "name": ven.name,
    "genres": ven.genres,
    "address": ven.address,
    "city": ven.city,
    "state": ven.state,
    "phone": ven.phone,
    "website": ven.website,
    "facebook_link": ven.facebook_link,
    "seeking_talent": ven.seeking_talent,
    "seeking_description": ven.seeking_description ,
    "image_link": ven.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        # insert form data as a new Venue record in the db, instead
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']
        genres = request.form.getlist('genres')
        if (request.form['seeking_talent'] == 'True'):
            seeking_talent = True
        else:
            seeking_talent = False
        seeking_description = request.form['seeking_description']
        image_link = request.form['image_link']
        website = request.form['website']

        venue = Venue.query.get(venue_id)
        venue.name = name
        venue.city = city
        venue.state = state
        venue.address = address
        venue.phone = phone
        venue.facebook_link = facebook_link
        venue.genres = genres
        venue.seeking_talent = seeking_talent
        venue.seeking_description = seeking_description
        venue.image_link = image_link
        venue.website = website
        db.session.commit()

    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    # if there error
    if error:
        flash('Venue ' + request.form['name'] + ' not listed!')
        abort(500)
    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully Updated!')
        return redirect(url_for('show_venue', venue_id=venue_id))


# venue record with ID <venue_id> using the new attributes

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        # insert form data as a new artist record in the db, instead
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']
        genres = request.form.getlist('genres')
        if (request.form['seeking_venue'] == 'True'):
            seeking_venue = True
        else:
            seeking_venue = False
        seeking_description = request.form['seeking_description']
        image_link = request.form['image_link']
        website = request.form['website']
        # modify data to be the data object returned from db insertion
        artist = Artist(name=name, city=city, state=state , phone=phone, facebook_link=facebook_link,
                      genres=genres, seeking_venue=seeking_venue, seeking_description=seeking_description,
                      image_link=image_link, website=website)
        db.session.add(artist)
        db.session.commit()

    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    # if there error
    if error:
        flash('Artist ' + request.form['name'] + ' not listed!')
        abort(500)
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
        return render_template('pages/home.html')

    # called upon submitting the new artist listing form

  # on successful db insert, flash success
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.all()
  data=[]
  for show in shows:
      data.append({
          "venue_id":show.venue_id,
          "venue_name":show.venue.name,
          "artist_id":show.artist_id,
          "artist_name":show.artist.name,
          "artist_image_link":show.artist.image_link,
          "start_time":show.start_date.strftime("%A %b %d %Y, %I:%M%p")

      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        # insert form data as a new artist record in the db, instead
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_date = request.form['start_time']

        # modify data to be the data object returned from db insertion
        show = Show(artist_id=artist_id, venue_id=venue_id, start_date=start_date)
        db.session.add(show)
        db.session.commit()

    except():
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    # if there error
    if error:
        flash('An error occurred. Show could not be listed.')
        abort(500)
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
