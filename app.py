# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    jsonify,
    abort,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
from sqlalchemy import func, or_

# Added to try to fix database connection
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://haileycarlson:cupcake@localhost:5432/fyyur"
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)
# Added to try to fix database connection
migrate = Migrate(app, db)

# Added to get the FLASK_APP command to work
app.app_context().push()

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


# shows = db.Table(
#     "shows",
#     db.Column("show_id", db.Integer, db.ForeignKey("show.id"), primary_key=True),
#     db.Column("artist_id", db.Integer, db.ForeignKey("artist.id"), primary_key=True),
#     db.Column("venue_id", db.Integer, db.ForeignKey("venue.id"), primary_key=True),
# )


class Show(db.Model):
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"))
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    artists = db.relationship(
        "Artist", secondary=shows, backref=db.backref("shows", lazy=True)
    )
    venues = db.relationship(
        "Venue", secondary=shows, backref=db.backref("shows", lazy=True)
    )


class Venue(db.Model):
    __tablename__ = "venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    # artist_upcoming_shows = db.relationship(
    #     "Artist", secondary=shows, backref=db.backref("upcoming_venues", lazy=True)
    # )
    # artist_past_shows = db.relationship(
    #     "Artist", secondary=shows, backref=db.backref("past_venues", lazy=True)
    # )

    # def upcoming_shows_count(self):
    #     now = datetime.utcnow()
    #     return len(
    #         [show for show in self.artist_upcoming_shows if show.start_time > now]
    #     )

    # def past_shows_count(self):
    #     now = datetime.utcnow()
    #     return len([show for show in self.artist_past_shows if show.start_time <= now])

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, genres: {self.genres}, city: {self.city}, state: {self.state}, address: {self.address}, phone: {self.phone}, website: {self.website}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, seeking_talent: {self.seeking_talent}, seeking_description: {self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))
    venue_past_shows = db.relationship(
        "Venue", secondary=shows, backref=db.backref("past_artists", lazy=True)
    )
    venue_upcoming_shows = db.relationship(
        "Venue", secondary=shows, backref=db.backref("upcoming_artists", lazy=True)
    )
    # # past_shows_count = db.func.count(Show.id)
    # # upcoming_shows_count = db.func.count(Show.id)

    def upcoming_shows_count(self):
        now = datetime.utcnow()
        return len(
            [show for show in self.venue_upcoming_shows if show.start_time > now]
        )

    def past_shows_count(self):
        now = datetime.utcnow()
        return len([show for show in self.venue_past_shows if show.start_time <= now])

    # def __repr__(self):
    #     return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, website: {self.website}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, seeking_venue: {self.seeking_venue}, see king_description: {self.seeking_description}, past_shows_count: {self.past_shows_count}, upcoming_shows_count: {self.upcoming_shows_count}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


db.create_all()

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    # data = [
    #     {
    #         "city": "San Francisco",
    #         "state": "CA",
    #         "venues": [
    #             {
    #                 "id": 1,
    #                 "name": "The Musical Hop",
    #                 "num_upcoming_shows": 0,
    #             },
    #             {
    #                 "id": 3,
    #                 "name": "Park Square Live Music & Coffee",
    #                 "num_upcoming_shows": 1,
    #             },
    #         ],
    #     },
    #     {
    #         "city": "New York",
    #         "state": "NY",
    #         "venues": [
    #             {
    #                 "id": 2,
    #                 "name": "The Dueling Pianos Bar",
    #                 "num_upcoming_shows": 0,
    #             }
    #         ],
    #     },
    # ]

    # return render_template("pages/venues.html", areas=data)
    #################################################################
    # MY CODE ~~~~~~~~~~~~~~~~~~

    venues = Venue.query.all()

    data = []

    for venue in venues:
        city_state_entry = next(
            (
                entry
                for entry in data
                if entry["city"] == venue.city and entry["state"] == venue.state
            ),
            None,
        )

        if city_state_entry:
            city_state_entry["venues"].append(
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": venue.upcoming_shows_count(),
                }
            )
        else:
            data.append(
                {
                    "city": venue.city,
                    "state": venue.state,
                    "venues": [
                        {
                            "id": venue.id,
                            "name": venue.name,
                            "num_upcoming_shows": venue.upcoming_shows_count(),
                        }
                    ],
                }
            )

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    #################################################################################
    # response = {
    #     "count": 1,
    #     "data": [
    #         {
    #             "id": 2,
    #             "name": "The Dueling Pianos Bar",
    #             "num_upcoming_shows": 0,
    #         }
    #     ],
    # }
    # return render_template(
    #     "pages/search_venues.html",
    #     results=response,
    #     search_term=request.form.get("search_term", ""),
    # )
    ###############################################################################
    # My Code

    search_term = request.form.get("search_term", "")

    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

    response = {
        "count": len(venues),
        "data": [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": venue.upcoming_shows_count(),
            }
            for venue in venues
        ],
    }

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [
    #         {
    #             "artist_id": 4,
    #             "artist_name": "Guns N Petals",
    #             "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #             "start_time": "2019-05-21T21:30:00.000Z",
    #         }
    #     ],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [
    #         {
    #             "artist_id": 5,
    #             "artist_name": "Matt Quevedo",
    #             "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #             "start_time": "2019-06-15T23:00:00.000Z",
    #         }
    #     ],
    #     "upcoming_shows": [
    #         {
    #             "artist_id": 6,
    #             "artist_name": "The Wild Sax Band",
    #             "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #             "start_time": "2035-04-01T20:00:00.000Z",
    #         },
    #         {
    #             "artist_id": 6,
    #             "artist_name": "The Wild Sax Band",
    #             "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #             "start_time": "2035-04-08T20:00:00.000Z",
    #         },
    #         {
    #             "artist_id": 6,
    #             "artist_name": "The Wild Sax Band",
    #             "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #             "start_time": "2035-04-15T20:00:00.000Z",
    #         },
    #     ],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d["id"] == venue_id, [data1, data2, data3]))[0]
    # return render_template("pages/show_venue.html", venue=data)

    #  MY CODE ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # print(venue_id)
    # print(venue[0])
    venue = Venue.query.get(venue_id)
    if venue:
        return render_template("pages/show_venue.html", venue=venue)
    else:
        return "Venue not found", 404


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form, meta={'csrf': False})
    # error = False
    # try:
    #     print(request.form)
    #     # genres = request.form.getlist('genres')
    #     # genres_str = ",".join(genres)
    #     seeking_value = False
    #     # seeking_talent = request.form['seeking_talent']
    #     seeking_talent = request.form.get("seeking_talent") == "y"
    #     if seeking_talent == "y":
    #         seeking_value = True
    #     else:
    #         seeking_value = False

    if form.validate():

      try:
        new_venue = Venue(
            name=form.name.data,
            genres=form.genres.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            website=form.website_link.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(new_venue)
        db.session.commit()

        # body["id"] = new_venue.id
        # body["name"] = new_venue.name
        # body["genres"] = new_venue.genres
        # body["city"] = new_venue.city
        # body["state"] = new_venue.state
        # body["address"] = new_venue.address
        # body["phone"] = new_venue.phone
        # body["website"] = new_venue.website
        # body["image_link"] = new_venue.image_link
        # body["facebook_link"] = new_venue.facebook_link
        # body["seeking_talent"] = new_venue.seeking_talent
        # body["seeking_description"] = new_venue.seeking_description
      except ValueError as e:
        db.session.rollback()
        print(e)

      finally:
        db.session.close()

      flash("Venue " + request.form["name"] + " was successfully listed!")
      return redirect(url_for("venues"))
        # return jsonify(body)
        

    else:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        return abort(500)


#  name = request.get_json()["name"]
#       genres = request.get_json()["genres"]
#       city = request.get_json()["city"]
#       state = request.get_json()["state"]
#       address = request.get_json()["address"]
#       phone = request.get_json()["phone"]
#       website = request.get_json()["website"]
#       image_link = request.get_json()["image_link"]
#       facebook_link = request.get_json()["facebook_link"]
#       seeking_talent = request.get_json()["seeking_talent"]
#       seeking_description = request.get_json()["seeking_description"]

# on successful db insert, flash success
# flash("Venue " + request.form["name"] + " was successfully listed!")
# TODO: on unsuccessful db insert, flash an error instead.
# e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
# return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    try:
        venue = Venue.query.get(venue_id)
        for Venue in venues:
            db.session.delete(venue)
            db.session.commit()
    except:
        db.session.close()
    if error:
        abort(500)
    else:
        return render_template("pages/home.html")


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    data = [
        {
            "id": 4,
            "name": "Guns N Petals",
        },
        {
            "id": 5,
            "name": "Matt Quevedo",
        },
        {
            "id": 6,
            "name": "The Wild Sax Band",
        },
    ]
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    # response = {
    #     "count": 1,
    #     "data": [
    #         {
    #             "id": 4,
    #             "name": "Guns N Petals",
    #             "num_upcoming_shows": 0,
    #         }
    #     ],
    # }

    search_term = request.form.get("search_term", "")

    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

    response = {
        "count": len(artists),
        "data": [
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": artist.upcoming_shows_count(),
            }
            for artist in artists
        ],
    }

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    # MY CODE !!!!!!!!!
    # return render_template(
    #   "pages/show_artist.html",
    #   artist=Artist.query.all(),
    #   active_artist=Artist.query.get(artist_id))

    data1 = {
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
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "past_shows": [
            {
                "venue_id": 1,
                "venue_name": "The Musical Hop",
                "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
                "start_time": "2019-05-21T21:30:00.000Z",
            }
        ],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 5,
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "past_shows": [
            {
                "venue_id": 3,
                "venue_name": "Park Square Live Music & Coffee",
                "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
                "start_time": "2019-06-15T23:00:00.000Z",
            }
        ],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 6,
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "past_shows": [],
        "upcoming_shows": [
            {
                "venue_id": 3,
                "venue_name": "Park Square Live Music & Coffee",
                "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
                "start_time": "2035-04-01T20:00:00.000Z",
            },
            {
                "venue_id": 3,
                "venue_name": "Park Square Live Music & Coffee",
                "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
                "start_time": "2035-04-08T20:00:00.000Z",
            },
            {
                "venue_id": 3,
                "venue_name": "Park Square Live Music & Coffee",
                "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
                "start_time": "2035-04-15T20:00:00.000Z",
            },
        ],
        "past_shows_count": 0,
        "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d["id"] == artist_id, [data1, data2, data3]))[0]
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist)
    # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    # }
    # TODO: populate form with fields from artist with ID <artist_id>

    if artist:
        form = ArtistForm(obj=artist)

        return render_template("forms/edit_artist.html", form=form, artist=artist)

    else:
        flash("Artist not found")
        return redirect(url_for("artist"))


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = request.form

    artist = Artist.query.get(artist_id)

    if artist:
        artist.name = form.get("name", artist.name)
        artist.genres = form.get("generes", artist.genres)
        artist.city = form.get("city", artist.city)
        artist.state = form.get("state", artist.state)
        artist.address = request.form("address", artist.address)
        artist.phone = request.form("phone", artist.phone)
        artist.website = request.form("website_link", artist.website)
        artist.image_link = request.form("image_link", artist.image_link)
        artist.facebook_link = request.form("facebook_link", artist.facebook_link)
        artist.seeking_venue = ("seeking_value", artist.seeking_venue)
        artist.seeking_description = request.form(
            "seeking_description", artist.seeking_description
        )
        try:
            db.session.commit()
            flash("Artist " + request.form["name"] + " was successfully updated!")

        finally:
            db.session.close()

        return redirect(url_for("show_artist", artist_id=artist_id))
    else:
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed."
        )
        return abort(500)


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    # }
    # TODO: populate form with values from venue with ID <venue_id>

    venue = Venue.query.get(venue_id)

    if venue:
        form = VenueForm(obj=venue)

        return render_template("forms/edit_venue.html", form=form, venue=venue)

    else:
        flash("Venue not found")
        return redirect(url_for("venues"))


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    form = request.form

    venue = Venue.query.get(venue_id)

    if venue:
        venue.name = form.get("name", venue.name)
        venue.genres = form.get("generes", venue.genres)
        venue.city = form.get("city", venue.city)
        venue.state = form.get("state", venue.state)
        venue.address = form.get("address", venue.address)
        venue.phone = form.get("phone", venue.phone)
        venue.website = form.get("website_link", venue.website)
        venue.image_link = form.get("image_link", venue.image_link)
        venue.facebook_link = form.get("facebook_link", venue.facebook_link)
        venue.seeking_talent = form.get("seeking_value")
        venue.seeking_description = form.get(
            "seeking_description", venue.seeking_description
        )

        try:
            db.session.commit()
            flash("Venue " + request.form["name"] + " was successfully updated!")

        finally:
            db.session.close()

        return redirect(url_for("show_venue", venue_id=venue_id))
    else:
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        return abort(500)


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        seeking_value = False
        seeking_venue = request.form["seeking_venue"]
        if seeking_venue == "y":
            seeking_value = True

        new_artist = Artist(
            name=request.form["name"],
            genres=request.form["genres"],
            city=request.form["city"],
            state=request.form["state"],
            address=request.form["address"],
            phone=request.form["phone"],
            website=request.form["website_link"],
            image_link=request.form["image_link"],
            facebook_link=request.form["facebook_link"],
            seeking_venue=seeking_value,
            seeking_description=request.form["seeking_description"],
        )
        db.session.add(new_artist)
        db.session.commit()

        # body["id"] = new_artist.id
        # body["name"] = new_artist.name
        # body["genres"] = new_artist.genres
        # body["city"] = new_artist.city
        # body["state"] = new_artist.state
        # body["address"] = new_artist.address
        # body["phone"] = new_artist.phone
        # body["website"] = new_artist.website
        # body["image_link"] = new_artist.image_link
        # body["facebook_link"] = new_artist.facebook_link
        # body["seeking_venue"] = new_artist.seeking_venue
        # body["seeking_description"] = new_artist.seeking_description
    except Exception as e:
        db.session.rollback()
        error = e
        print(sys.exc_info())
        print(e)

    finally:
        db.session.close()

    if error:
        # flash('An error occurred. Artist ' + request.form["name"] + ' could not be listed.')
        return abort(500)

    else:
        flash("Artist " + request.form["name"] + " was successfully listed!")
        return render_template("pages/artist.html", shows=data)

    # on successful db insert, flash success
    # flash("Artist " + request.form["name"] + " was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [
        {
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z",
        },
    ]
    return render_template("pages/shows.html", shows=data)


# MY CODE !!!!!!!!!!!!
# def index():
#     shows = shows.query.all()
#     return render_template("pages/shows.html", shows=shows)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash("Show was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

    try:
        # Grabs the info from form to be added to the db

        new_show = Show(
            start_time=request.form["start_time"],
            artist_id=request.form["artist_id"],
            venue_id=request.form["venue_id"],
            artists=request.form["artists"],
            venues=request.form["venues"],
        )

        # Info is then added to the db and commited

        db.session.add(new_show)
        db.session.commit()

    # If adding data to the db goes wrong the session rollsback to not add data and sends errror message

    except Exception as e:
        db.session.rollback()
        error = e
        print(sys.exc_info())
        print(e)

    # Closes the db session since we are done adding data

    finally:
        db.session.close()

    if error:
        flash("An error occurred. Your show could not be listed.")
        return abort(500)

    else:
        flash("Your show was successfully listed!")

    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run(debug=True)

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
