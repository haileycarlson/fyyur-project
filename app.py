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

from models import db, Show, Venue, Artist

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
# Connecting to local DB
app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://haileycarlson:cupcake@localhost:5432/fyyur"
moment = Moment(app)
app.config.from_object("config")
db.init_app(app)

# Added to try to fix database connection
migrate = Migrate(app, db)

# Added to get the FLASK_APP command to work
app.app_context().push()


# db.create_all()

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
    # Queries all the venue data
    venues = Venue.query.all()

    # Initializes an empyt list to store venue data
    data = []

    for venue in venues:
      # Calculating the count of upcoming shows for each venue
        upcoming_shows_count = (Show.query.join(Venue)
          .filter(
            Show.venue_id == venue.id,
            Show.start_time > datetime.utcnow()
          )
          .count()
          )

        # Checks to see if a city-state entry for the venue already exists in data
        city_state_entry = next(
            (
                entry
                for entry in data
                if entry["city"] == venue.city and entry["state"] == venue.state
            ),
            None,
        )

        if city_state_entry:
            # If the city-state entry exists, appends venue details to the venue lists
            city_state_entry["venues"].append(
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": upcoming_shows_count,
                }
            )
        else:
            # If the city-state entry does not exists, adds a new entry to the venue details
            data.append(
                {
                    "city": venue.city,
                    "state": venue.state,
                    "venues": [
                        {
                            "id": venue.id,
                            "name": venue.name,
                            "num_upcoming_shows": upcoming_shows_count,
                        }
                    ],
                }
            )

    # Renders the venues page with the collected venue data
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # Grabs the search term from the form data
    search_term = request.form.get("search_term", "")

    # Queries the venue based on search term using case-insensitive matching
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()

    # Returns a response dictionary with count and data of searched venue
    response = {
        "count": len(venues),
        "data": venues
    }

    # Renders the search page with response data and search term
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # Queries the venue by ID
    venue = Venue.query.get(venue_id)

    # Checks to see if artist exists
    if venue:
      # empty lists for the past and upcoming shows
      past_shows = []
      upcoming_shows = []

      # Gets the current time
      current_time = datetime.now()

    # Iterating through the venue shows to put into past or present shows
    for show in venue.shows:
      if show.start_time < current_time:
        past_shows.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

      else:
        upcoming_shows.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

    # Creatingg a dictionary with venue and show details
    data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "city": venue.city,
      "state": venue.state,
      "address": venue.address,
      "phone": venue.phone,
      "website": venue.website,
      "image_link": venue.image_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description, 
      "upcoming_shows": upcoming_shows,
      "upcoming_shows_count": len(upcoming_shows),
      "past_shows": past_shows,
      "past_shows_count": len(past_shows)
    }

    # Renders the show venue page with details of the venue and shows
    if venue:
        return render_template("pages/show_venue.html", venue=data)
    else:
        # Returns error message if the venue is not found
        return "Venue not found", 404


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
  # Grabs the venue form template to be filled out
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    #  Creating an Venue form instance form from form data and disabling CSRF protection
    form = VenueForm(request.form, meta={'csrf': False})
    
    # Validating form data before it is proccessed and added to database
    if form.validate():

      # Inserting a new venue record into database
      try:
        # New venue object is created based on form data
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
        # Adding new venue to database session
        db.session.add(new_venue)
        # Commiting changes to the database
        db.session.commit()

      # Handles exceptions that may occur during database operations
      except Exception as e:
         # Rolls back changes if exception or any other problems occur
        db.session.rollback()
        print(sys.exc_info)
        print(e)

      # Closes database connection regardless of success or not
      finally:
        db.session.close()


      # Flashing success message if venue is successfully added and redirecting to new venue page
      flash("Venue " + request.form["name"] + " was successfully listed!")
      return redirect(url_for("venues"))
        
        

    else:
      # Flashing an error message if venue was not successfully added
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        return abort(500)


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    
    error = False
    try:
        venue = Venue.query.get(venue_id)
        for venue in venues:
          db.session.delete(venue)
          db.session.commit()
          flash(f"Venue {venue_id} was successfully deleted!")
    except: 
          db.session.close()
    if error:
      db.session.rollback()
      flash(f"An error occured while deleting Venue {venue_id}. Error: {str(e)}")
      abort(500)
    else:
      return render_template("pages/home.html")


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # Queries all the artist data 
    artist = Artist.query.all()

    # Returns all data for all artists in database
    return render_template("pages/artists.html", artists=artist)

@app.route("/artists/search", methods=["POST"])
def search_artists():
    # Grabs the search term from the form data
    search_term = request.form.get("search_term", "")

    # Queries the artist based on search term using case-insensitive matching
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()

    # Returns a response dictionary with count and data of searched artsit
    response = {
      "count": len(artists),
      "data": artists
    }
    # Renders the search page with response data and search term
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # Queries the artist by ID
    artist = Artist.query.get(artist_id)

    # Checks to see if artist exists
    if artist:
      # empty lists for the past and upcoming shows
      past_shows = []
      upcoming_shows = []

      # Gets the current time
      current_time = datetime.now()

    # Iterating through the artist shows to put into past or present shows
    for show in artist.shows:
      if show.start_time < current_time:
        past_shows.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })

      else:
        upcoming_shows.append({
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
        })
    # Creatingg a dictionary with artist and show details
    data = {
        "id": artist.id,
        "name": artist.name,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "genres": artist.genres,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows),
        "past_shows": past_shows,
        "past_shows_count": len(past_shows)
    }


    if artist:
      # Renders the show artist page with details of the artist and shows
        return render_template("pages/show_artist.html", artist=data)
    else:
      # Returns error message if the artist is not found
        return "Artist not found", 404

#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    # Gets an empty form to edit artist
    form = ArtistForm(obj=artist)

    # Querys the artist by its ID
    artist = Artist.query.get(artist_id)

    # Checks to see if artist exists
    if artist:
        # Populates the details from the artist to edit
        form = ArtistForm(obj=artist)

        # Adds the details from the artist to the form to edit
        return render_template("forms/edit_artist.html", form=form, artist=artist)

    else:
       # Flashes error message if the venue is not found
        flash("Artist not found")
        return redirect(url_for("artist"))


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # Grabs form data for editing artist details
    form = request.form

    # Querys the artist by ID
    artist = Artist.query.get(artist_id)

    # Checks if artist exists
    if artist:
        artist.name = form.get("name", artist.name)
        artist.genres = form.get("generes", artist.genres)
        artist.city = form.get("city", artist.city)
        artist.state = form.get("state", artist.state)
        artist.phone = form.get("phone", artist.phone)
        artist.website = form.get("website_link", artist.website)
        artist.image_link = form.get("image_link", artist.image_link)
        artist.facebook_link = form.get("facebook_link", artist.facebook_link)
        artist.seeking_venue = form.get("seeking_value", artist.seeking_venue)
        artist.seeking_description = form.get(
            "seeking_description", artist.seeking_description
        )
        try:
            # Committing changes to database
            db.session.commit()
            flash("Artist " + request.form["name"] + " was successfully updated!")

        finally:
            # Closes database session
            db.session.close()
        # Redirects to the venue page after successfully updating
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
    # Gets an empty form to edit venue
    form = VenueForm()
    
    # Querys the venue by its ID
    venue = Venue.query.get(venue_id)

    # Checks to see if venue exists
    if venue:
        # Populates the details from the venue to edit
        form = VenueForm(obj=venue)

        # Adds the details from the venue to the form to edit
        return render_template("forms/edit_venue.html", form=form, venue=venue)

    else:
        # Flashes error message if the venue is not found
        flash("Venue not found")
        return redirect(url_for("venues"))


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # Grabs form data for editing venue details
    form = request.form

    # Querys the venue by ID
    venue = Venue.query.get(venue_id)

    # Checks if venue exists
    if venue:
        # Updates the venue attributes based on form data
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
            # Committing changes to database
            db.session.commit()
            flash("Venue " + request.form["name"] + " was successfully updated!")

        finally:
            # Closes database session
            db.session.close()
        
        # Redirects to the venue page after successfully updating 
        return redirect(url_for("show_venue", venue_id=venue_id))
    else:
        # Flashes error if the venue can not be found or updated
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        return abort(500)


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
  # Grabs the artist form template to be filled out 
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
  #  Creating an Artist form instance form from form data and disabling CSRF protection
    form = ArtistForm(request.form, meta={'csrf': False})

    # Validating form data before it is proccessed and added to database
    if form.validate():

      # Inserting a new artist record into database
      try:
        # New artist object is created based on form data
        new_artist = Artist(
            name=form.name.data,
            genres=form.genres.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            website=form.website_link.data,
            image_link=form.image_link.data,
            facebook_link=form.facebook_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
        )
        # Adding new artist to database session
        db.session.add(new_artist)
        # Commiting changes to the database
        db.session.commit()

      # Handles exceptions that may occur during database operations
      except Exception as e:
        # Rolls back changes if exception or any other problems occur
        db.session.rollback()
        print(sys.exc_info())
        print(e)

      # Closes database connection regardless of success or not
      finally:
        db.session.close()

      # Flashing success message if artist is successfully added and redirecting to new artist page
      flash("Artist " + request.form["name"] + " was successfully listed!")
      return redirect(url_for("artists"))
       
    else:
      # Flashing an error message if artist was not successfully added 
        flash(
            "An error occurred. Artist " + request.form["name"] + " could not be listed." 
        )    
    return abort(500)


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():

    shows = Show.query.all()

    data = []

    for show in shows:
      data.append(
        {
          "venue_id": show.venue.id,
          "venue_name": show.venue.name,
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time.isoformat()
        }
      )    

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():

    form = ShowForm(request.form, meta={'csrf': False})

    if form.validate():

      try:
        # Grabs the info from form to be added to the db

          new_show = Show(
              start_time=form.start_time.data,
              artist_id=form.artist_id.data,
              venue_id=form.venue_id.data,
              # artists=form.artists.data,
              # venues=form.venues.data,
          )

        # Info is then added to the db and commited

          db.session.add(new_show)
          db.session.commit()

    # If adding data to the db goes wrong the session rollsback to not add data and sends errror message

      except Exception as e:
        db.session.rollback()
        # error = e
        print(sys.exc_info())
        print(e)

    # Closes the db session since we are done adding data

      finally:
        db.session.close()

      flash("Your show was successfully listed!")
      return render_template("pages/home.html")

       

    else:
        flash("An error occurred. Your show could not be listed.")
        return abort(500)

       


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
