"""
Database models for the Movie Recommendation System
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Movie(db.Model):
    """Movie model to store movie information"""
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=True)  # The Movie Database ID
    title = db.Column(db.String(255), nullable=False, index=True)
    genre = db.Column(db.Text, nullable=True)
    overview = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)  # Combined genre + overview for ML
    release_date = db.Column(db.Date, nullable=True)
    poster_url = db.Column(db.String(500), nullable=True)
    imdb_rating = db.Column(db.Float, nullable=True)
    popularity = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    ratings = db.relationship('UserRating', backref='movie', lazy='dynamic', cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', foreign_keys='Recommendation.recommended_movie_id', 
                                    backref='recommended_movie', lazy='dynamic')
    
    def __repr__(self):
        return f'<Movie {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tmdb_id': self.tmdb_id,
            'title': self.title,
            'genre': self.genre,
            'overview': self.overview,
            'release_date': self.release_date.isoformat() if self.release_date else None,
            'poster_url': self.poster_url,
            'imdb_rating': self.imdb_rating,
            'popularity': self.popularity
        }

class User(db.Model):
    """User model for authentication and personalization"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    ratings = db.relationship('UserRating', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    recommendation_history = db.relationship('RecommendationHistory', backref='user', 
                                           lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class UserRating(db.Model):
    """User ratings for movies"""
    __tablename__ = 'user_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)  # 1.0 to 5.0
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint to prevent duplicate ratings
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='user_movie_rating'),)
    
    def __repr__(self):
        return f'<UserRating {self.user.username}: {self.movie.title} - {self.rating}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Recommendation(db.Model):
    """Pre-computed movie recommendations based on content similarity"""
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    source_movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    recommended_movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    rank = db.Column(db.Integer, nullable=False)  # 1-10 ranking
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    source_movie = db.relationship('Movie', foreign_keys=[source_movie_id], backref='source_recommendations')
    
    # Unique constraint and index for performance
    __table_args__ = (
        db.UniqueConstraint('source_movie_id', 'recommended_movie_id', name='unique_recommendation'),
        db.Index('idx_source_movie_rank', 'source_movie_id', 'rank')
    )
    
    def __repr__(self):
        return f'<Recommendation {self.source_movie.title} -> {self.recommended_movie.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_movie_id': self.source_movie_id,
            'recommended_movie_id': self.recommended_movie_id,
            'similarity_score': self.similarity_score,
            'rank': self.rank,
            'recommended_movie': self.recommended_movie.to_dict() if self.recommended_movie else None
        }

class RecommendationHistory(db.Model):
    """Track user's recommendation requests and interactions"""
    __tablename__ = 'recommendation_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for anonymous users
    session_id = db.Column(db.String(255), nullable=True)  # For anonymous tracking
    source_movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    clicked_recommendation_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    source_movie = db.relationship('Movie', foreign_keys=[source_movie_id])
    clicked_movie = db.relationship('Movie', foreign_keys=[clicked_recommendation_id])
    
    def __repr__(self):
        return f'<RecommendationHistory {self.source_movie.title} at {self.created_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'source_movie_id': self.source_movie_id,
            'clicked_recommendation_id': self.clicked_recommendation_id,
            'created_at': self.created_at.isoformat(),
            'source_movie': self.source_movie.to_dict() if self.source_movie else None,
            'clicked_movie': self.clicked_movie.to_dict() if self.clicked_movie else None
        }

class SimilarityMatrix(db.Model):
    """Store the computed similarity matrix for efficient lookups"""
    __tablename__ = 'similarity_matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    movie1_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    movie2_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    similarity_score = db.Column(db.Float, nullable=False)
    algorithm = db.Column(db.String(50), default='cosine_similarity')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    movie1 = db.relationship('Movie', foreign_keys=[movie1_id])
    movie2 = db.relationship('Movie', foreign_keys=[movie2_id])
    
    # Indexes for performance
    __table_args__ = (
        db.UniqueConstraint('movie1_id', 'movie2_id', name='unique_movie_pair'),
        db.Index('idx_movie1_similarity', 'movie1_id', 'similarity_score'),
        db.Index('idx_movie2_similarity', 'movie2_id', 'similarity_score')
    )
    
    def __repr__(self):
        return f'<SimilarityMatrix {self.movie1.title} <-> {self.movie2.title}: {self.similarity_score}>'