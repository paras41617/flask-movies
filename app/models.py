from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    ratings = db.relationship('Rating', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
    def is_active(self):
        """True, as all users are active."""
        return True
    
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.Date)
    director = db.Column(db.String(255))
    genre = db.Column(db.String(100))
    average_rating = db.Column(db.Float)
    ticket_price = db.Column(db.Float)
    cast = db.Column(db.String(255))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ratings = db.relationship('Rating', backref='movie', lazy=True)

    def serialize(self):
        ratings = [rating.rating for rating in self.ratings]
        num_ratings = len(ratings)
        average_rating = sum(ratings) / num_ratings if num_ratings > 0 else None

        # Custom serialization for Rating objects
        def serialize_rating(rating):
            return {
                'user_id': rating.user_id,
                'rating': rating.rating
            }

        serialized_ratings = [serialize_rating(rating) for rating in self.ratings]

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'director': self.director,
            'genre': self.genre,
            'average_rating': average_rating,
            'ticket_price': self.ticket_price,
            'cast': self.cast,
            'num_ratings': num_ratings,
            'ratings': serialized_ratings
        }
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)

