#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for ,jsonify
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app , db)
## TOTO_done: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#




class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer , primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(1000))
    website_link = db.Column(db.String(500))
    is_seeking_talent=db.Column(db.Boolean)
    seeking_talent_desck = db.Column(db.String(1000))
    
    artists = db.relationship('Shows' , backref = 'shows_venues' )
    
    def __repr__(self):
        return f'Venue:<id:{self.id},name:{self.name},city:{self.city},state:{self.state},address:{self.address},phone:{self.phone},image_link:{self.image_link},facebookLink:{self.facebook_link},genres:{self.genres},Website_link:{self.website_link},is_seeking_talent:{self.is_seeking_talent},seeking_desc={self.seeking_talent_desck}>'
    @property
    def serialize(self):
        allShows = Shows.query.filter_by(venues=self.id).count()
        boolVal = False
         
        return {
            'id':self.id , 
            'name':self.name,
            'city':self.city,
            'state':self.state,
            'address':self.address,
            'phone':self.phone , 
            'image_link':self.image_link , 
            'facebook_link':self.facebook_link  , 
            'num_upcoming_shows':allShows , 
            'genres':self.genres , 
            'website_link':self.website_link , 
            'is_seeking_talent':boolVal , 
            'seeking_desc':self.seeking_talent_desck 
        }
    @property
    def searchSerialize(self):
        allShows = Shows.query.filter_by(venues=self.id).count()
        return {
            'id':self.id , 
            'name':self.name , 
            'num_upcoming_shows':allShows,
            
        }
        
    @property
    def local(self):
        return {
            'city':self.city , 
            'state':self.state,
        }

    @property 
    def pastShows(self):
        shows = Shows.query.filter_by(venues=self.id).filter(Shows.start_time < datetime.now()).all()        
        allResults = [] 
        for s in shows:
            result = {
                "artist_id":s.artist.id  , 
                "artist_name":s.artist.name , 
                "artist_image_link":s.artist.image_link , 
                "start_time":s.start_time  , 
            }
            allResults.append(result)
        return {
            "count":len(shows) , 
            "allShows":allResults , 
            
        }
        
    @property 
    def comingShows(self):
        shows = Shows.query.filter_by(venues=self.id).filter(Shows.start_time > datetime.now()).all()
        showsCount = Shows.query.filter_by(venues=self.id).count()
        allResults = [] 
        for s in shows:
            result = {
                "artist_id":s.artist.id  , 
                "artist_name":s.artist.name , 
                "artist_image_link":s.artist.image_link , 
                "start_time":s.start_time  , 
            }
            allResults.append(result)
        return {
            "count":len(shows) , 
            "allShows":allResults , 
            
        }

    @property
    def serializeAlData(self):
        venue = self
        result = venue.serialize 
        result["past_shows"] = venue.pastShows['allShows']
        result["upcoming_shows"] = venue.comingShows['allShows']
        result["past_shows_count"] = venue.pastShows['count']
        result["upcoming_shows_count"] = venue.comingShows['count']
        return result 
    
    ## TOTO_done: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    venues = db.relationship('Shows' , backref='shows_artists' , lazy=True)
    def __repr__(self):
        return f'Artist:<id:{self.id},name:{self.name},city:{self.city},state:{self.state},phone:{self.phone},genres:{self.genres},image_link:{self.image_link},facebook_link:{self.facebook_link}>'

    @property 
    def getArtistJson(self):
      return {
        "id":self.id , 
        "name":self.name , 
        "city":self.city , 
        "state":self.state , 
        "phnoe":self.phone , 
        "genres":self.genres , 
        "image_link":self.image_link , 
        "facebook_link":self.facebook_link
        
      }
    
    
    #   "past_shows": [{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }]
    @property 
    def getPastShows(self):
         
          shows = Shows.query.filter_by(artists=self.id).filter(Shows.start_time < datetime.now()).all()
          
          
          result = []
          for show in shows:
                tempResult = {
                  "venue_id":show.venue.id , 
                  "venue_name":show.venue.name , 
                  "venue_image_link":show.venue.image_link , 
                  "start_time":show.start_time
                }
                result.append(tempResult)
          return  {
            "count":len(shows) , 
            "allShows":result
            } 
    @property 
    def getComingShows(self):
         
          shows = Shows.query.filter_by(artists=self.id).filter(Shows.start_time > datetime.now()).all()
          result = []
          for show in shows:
                tempResult = {
                  "venue_id":show.venue.id , 
                  "venue_name":show.venue.name , 
                  "venue_image_link":show.venue.image_link , 
                  "start_time":show.start_time
                }
                result.append(tempResult)
          return {
            "count":len(shows) , 
            "allShows":result
            } 


class Shows(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer , primary_key=True , autoincrement=True)
    venues = db.Column(db.Integer , db.ForeignKey('venue.id') , primary_key=True )
    artists = db.Column (db.Integer , db.ForeignKey('artist.id') , primary_key=True)
    start_time = db.Column(db.DateTime)
    artist = db.relationship('Artist' , backref='venues1') 
    venue = db.relationship('Venue' , backref='artists1')
    def __repr__(self):
        return f'Show<id:{self.id},venuue:{self.venues} , artists:{self.artists},artist:{self.artist},venue={self.venue}>'
 
# TOTO_Done Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

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
    
    allLocs = Venue.query.distinct(Venue.city , Venue.state).all()
    data = []
    for loc in allLocs:
         data.append(loc.local)
    for d in data:
        d["venues"] = []
        allVens = Venue.query.filter_by(city=d['city'],state=d['state']).all()
        for v in allVens:
            #print(v)
            d["venues"].append(v.serialize)
        print(data)
        print("############## New Item ###############")
    return render_template('pages/venues.html', areas=data);
          
    
  # TOTO_Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  # data=[{
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]
  


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TOTO_Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
    data = Venue.query.filter(Venue.name.ilike('%V%'))
    searhcVenues = [] 
    for d in data:
        searhcVenues.append(d.searchSerialize)
    searchResult={"count":data.count() , 
                        "data":searhcVenues ,                          
                         }
    print ("😇😇😇😇😇😇😇😇😇😇😇")
    print (searchResult)
    return render_template('pages/search_venues.html', results=searchResult, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TOTO_Done: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  venue = Venue.query.get(venue_id)
  data = venue.serializeAlData
  print ("🍦🍦🍦🍦🍦🍦🍦🍦🍦🍦🍦")
  print (data)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
 
  
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TOTO_Done: insert form data as a new Venue record in the db, instead
  # Toto_Done: modify data to be the data object returned from db insertion
 try:
    isSeeking = request.form['seeking_talent']
    isSeekingBoolean = False 
    if isSeeking == 'y':
          isSeekingBoolean = True
    venue = Venue(name=request.form['name'], 
                  city=request.form['city'],
                  state=request.form['state'],
                  address=request.form['address'],
                  phone=request.form['phone'],
                  genres= request.form.getlist('genres'),
                  image_link = request.form['image_link'] , 
                  facebook_link=request.form['facebook_link'] , 
                  website_link = request.form['website_link'] , 
                  is_seeking_talent = isSeekingBoolean , 
                  seeking_talent_desck = request.form['seeking_description']
                  
                  
                  )
    print(venue)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
 except:
   flash( sys.exc_info() )
   db.session.rollback()
 finally:
   db.session.close()
 return render_template('pages/home.html')
 
  
  # on successful db xinsert, flash success
 
  # Toto_Done: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TOTO_done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    print('🛹✋🏻✋🏻✋🏻✋🏻✋🏻✋🏻✋🏻✋🏻✋🏻✋🏻')
    print(sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TOTO_Done: replace with real data returned from querying the database
  artists = Artist.query.all()
  result = [] 
  for artist in artists:
       result.append({
         "id":artist.id ,
         "name":artist.name ,  
         
       }) 
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=result )

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TOTO_Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searchStr = search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike("%{}%".format(searchStr))).all()
  allArtistsResult = [] 
  for artist in artists:
        shows = Shows.query.filter_by(artists=artist.id).filter(Shows.start_time > datetime.now()).all()
        artistJson = {
          "id":artist.id , 
          "name":artist.name , 
          "num_upcoming_shows":len(shows)
        }
        allArtistsResult.append(artistJson)
  result = {
    "count":len (artists) , 
    "data":allArtistsResult
  }
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  #}
  return render_template('pages/search_artists.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TOTO_done: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  result = artist.getArtistJson
  result["past_shows"] = artist.getPastShows['allShows']
  result["upcoming_shows"]=artist.getComingShows['allShows']
  result["past_shows_count"]=artist.getPastShows['count']
  result["upcoming_shows_count"]=artist.getComingShows['count']
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name = artist.name 
  form.genres = artist.genres 
  form.city = artist.city
  form.state = artist.artist
  form.phone = artist.phone
  form.image_link = artist.image_link
  
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TOTO_Done: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TOTO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)   
  artist.name=request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state'] 
  artist.phone = request.form['phone'] 
  artist.genres = request.form.getlist('genres') 
  artist.image_link = request.form.getlist('genres')  
  artist.facebook_link = request.form['facebook_link']
  try:
    db.session.commit()
  except:
    print (sys.exec_prefix)
  finally:
    db.session.close()
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  print('⛱⛱⛱⛱⛱⛱⛱')
  print('hassan venue edit')
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TOTO_done: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  print('🚥🚥🚥🚥🚥🚥🚥🚥🚥🚥')
  if venue.is_seeking_talent == None or venue.is_seeking_talent == 'f':
        venue.is_seeking_talent = False
  else:
        venue.is_seeking_talent = True
  print(venue)
  form.genres.data=venue.genres 
  # form.name = venue.name
  # form.genres = venue.genres
  # form.address = venue.address
  # form.city = venue.city
  # form.state = venue.state
  # form.phone = venue.phone
  # form.facebook_link = venue.facebook_link
  # form.image_link = venue.image_link
  #venue = Venue(id = 10 , name='Hassan')
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TOTO_Done: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
    #   isSeeking = request.form['seeking_talent']
    # isSeekingBoolean = False 
    # if isSeeking == 'y':
    #       isSeekingBoolean = True
    # venue = Venue(name=request.form['name'], 
    #               city=request.form['city'],
    #               state=request.form['state'],
    #               address=request.form['address'],
    #               phone=request.form['phone'],
    #               genres= request.form.getlist('genres'),
    #               image_link = request.form['image_link'] , 
    #               facebook_link=request.form['facebook_link'] , 
    #               website_link = request.form['website_link'] , 
    #               is_seeking_talent = isSeekingBoolean , 
    #               seeking_talent_desck = request.form['seeking_description']
  venue = Venue.query.get(venue_id)
  isSeeking = request.form['seeking_talent']
  isSeekingBoolean = False 
  if isSeeking == 'y':
     isSeekingBoolean = True
  venue.name=request.form['name'] 
  venue.city=request.form['city']
  venue.state=request.form['state']
  venue.address=request.form['address']
  venue.phone=request.form['phone']
  venue.image_link= request.form['image_link']
  venue.facebook_link=request.form['facebook_link']
  venue.genres = request.form.getlist('genres')
  venue.website_link = request.form['website_link']
  venue.is_seeking_talent=isSeekingBoolean
  venue.seeking_talent_desck = request.form['seeking_description']
  print('🎡🎡🎡🎡🎡🎡🎡🎡🎡')
  print(venue)
  try:
    db.session.commit() 
  except:
    print(sys.exc_info)
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
  # TOTO_Done: insert form data as a new Venue record in the db, instead
  # TOTO_Done: modify data to be the data object returned from db insertio
    try:
      artist = Artist(
      name=request.form['name'],
      city = request.form['city'],
      state = request.form['state'] , 
      phone = request.form['phone'] , 
      genres = request.form.getlist('genres') , 
      image_link = request.form.getlist('genres')  , 
      facebook_link = request.form['facebook_link']
      ) ; 
      print(artist)
      db.session.add(artist)
      db.session.commit()
    except:
      db.session.rollback()
      print ("Error inserting artist" + sys.exc_info())
      flash("Error inserting record")
    finally:
      db.session.close()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TOTO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # 
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TOTO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Shows.query.all()
  allShows = [] 
  for show in shows:
        showJson = {
              "venue_id": show.venue.id,
              "venue_name": show.venue.name,
              "artist_id": show.artist.id,
              "artist_name": show.artist.name,
              "artist_image_link": show.artist.image_link,
              "start_time": show.start_time
        }
        allShows.append(showJson)
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=allShows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TOTO_Done: insert form data as a new Show record in the db, instead
  try:
    print (request.form['venue_id'])
    print (request.form['artist_id'])
    venue = Venue.query.get(request.form['venue_id'])
    artist = Artist.query.get(request.form['artist_id'])
    show = Shows(start_time=request.form['start_time'])
    show.venue = venue 
    show.artist = artist
    print (show)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    print( sys.exc_info())
    db.session.rollback()
  finally:
    db.session.close()
  # on successful db insert, flash success
  
  # TOTO_Done: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
