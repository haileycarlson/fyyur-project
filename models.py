from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class Show(db.Model):
    __tablename__ = "show"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    # artist = db.relationship('Artist', backref='shows', lazy='joined')
    # venue = db.relationship('Venue', backref='shows', lazy='joined')


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
    shows = db.relationship("Show", backref="venue", cascade="all, delete-orphan", lazy=True)


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
    shows = db.relationship("Show", backref="artist", cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, city: {self.city}, state: {self.state}, phone: {self.phone}, website: {self.website}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, seeking_venue: {self.seeking_venue}, seeking_description: {self.seeking_description}>'
