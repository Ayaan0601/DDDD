import os
import pickle
import logging
from flask import Flask, render_template, jsonify, request, session
from werkzeug.middleware.proxy_fix import ProxyFix
from models import db, Movie, User, UserRating, Recommendation, RecommendationHistory, SimilarityMatrix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "movie-recommender-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
db.init_app(app)

# Global variables to store loaded data
movie_data = None
similarity_matrix = None

def load_data():
    """Load pickle files containing movie data and similarity matrix"""
    global movie_data, similarity_matrix
    
    try:
        # Load movie list
        if os.path.exists('movie_list.pkl'):
            with open('movie_list.pkl', 'rb') as f:
                movie_data = pickle.load(f)
            app.logger.info(f"Loaded {len(movie_data)} movies from movie_list.pkl")
        else:
            app.logger.error("movie_list.pkl not found")
            return False
            
        # Load similarity matrix
        if os.path.exists('similarity.pkl'):
            with open('similarity.pkl', 'rb') as f:
                similarity_matrix = pickle.load(f)
            app.logger.info(f"Loaded similarity matrix with shape: {similarity_matrix.shape}")
        else:
            app.logger.error("similarity.pkl not found")
            return False
            
        return True
        
    except Exception as e:
        app.logger.error(f"Error loading data files: {str(e)}")
        return False

# Create database tables and load data on startup
with app.app_context():
    try:
        db.create_all()
        app.logger.info("Database tables created successfully")
    except Exception as e:
        app.logger.error(f"Error creating database tables: {str(e)}")

# Load data on startup
data_loaded = load_data()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/movies')
def get_movies():
    """API endpoint to get list of all movie titles"""
    try:
        # Try to get movies from database first
        movies = Movie.query.order_by(Movie.title).all()
        
        if movies:
            movie_list = [movie.title for movie in movies]
            return jsonify({
                'movies': movie_list,
                'count': len(movie_list),
                'source': 'database'
            })
        
        # Fallback to pickle file if database is empty
        if not data_loaded or movie_data is None:
            return jsonify({
                'error': 'Movie data not available. Please ensure movie_list.pkl exists or database is populated.'
            }), 500
        
        # Extract movie titles and sort them from pickle
        movie_titles = sorted(movie_data['title'].tolist())
        return jsonify({
            'movies': movie_titles,
            'count': len(movie_titles),
            'source': 'pickle'
        })
        
    except Exception as e:
        app.logger.error(f"Error getting movies: {str(e)}")
        return jsonify({'error': 'Failed to retrieve movie list'}), 500

@app.route('/api/recommend', methods=['POST'])
def recommend_movies():
    """API endpoint to get movie recommendations"""
    try:
        data = request.get_json()
        if not data or 'movie' not in data:
            return jsonify({'error': 'Movie title is required'}), 400
        
        selected_movie = data['movie']
        
        # Try to get recommendations from database first
        source_movie = Movie.query.filter_by(title=selected_movie).first()
        
        if source_movie:
            # Get recommendations from database
            db_recommendations = Recommendation.query.filter_by(
                source_movie_id=source_movie.id
            ).order_by(Recommendation.rank).limit(10).all()
            
            if db_recommendations:
                recommendations = []
                for rec in db_recommendations:
                    recommendations.append({
                        'title': rec.recommended_movie.title,
                        'similarity_score': round(float(rec.similarity_score), 4)
                    })
                
                # Log recommendation request for analytics
                try:
                    history = RecommendationHistory(
                        source_movie_id=source_movie.id,
                        session_id=session.get('session_id'),
                        user_agent=request.headers.get('User-Agent'),
                        ip_address=request.remote_addr
                    )
                    db.session.add(history)
                    db.session.commit()
                except Exception as e:
                    app.logger.warning(f"Failed to log recommendation request: {str(e)}")
                
                return jsonify({
                    'selected_movie': selected_movie,
                    'recommendations': recommendations,
                    'source': 'database'
                })
        
        # Fallback to pickle-based recommendations if database doesn't have the movie
        if not data_loaded or movie_data is None or similarity_matrix is None:
            return jsonify({
                'error': 'Movie not found in database and pickle-based recommendations not available.'
            }), 404
        
        # Find the movie in the pickle dataset
        movie_matches = movie_data[movie_data['title'] == selected_movie]
        if movie_matches.empty:
            return jsonify({'error': f'Movie "{selected_movie}" not found in database or pickle data'}), 404
        
        # Get the index of the selected movie in pickle data
        movie_index = movie_matches.index[0]
        
        # Calculate similarity scores for all movies
        similarity_scores = list(enumerate(similarity_matrix[movie_index]))
        
        # Sort by similarity score (descending) and exclude the selected movie itself
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top 10 recommendations (excluding the first one which is the movie itself)
        recommended_indices = [i[0] for i in similarity_scores[1:11]]
        
        # Get movie titles for recommendations
        recommendations = []
        for i, idx in enumerate(recommended_indices):
            movie_title = movie_data.iloc[idx]['title']
            similarity_score = similarity_scores[i + 1][1]  # Get score from sorted list
            recommendations.append({
                'title': movie_title,
                'similarity_score': round(float(similarity_score), 4)
            })
        
        return jsonify({
            'selected_movie': selected_movie,
            'recommendations': recommendations,
            'source': 'pickle'
        })
        
    except Exception as e:
        app.logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Check database connectivity
        db_status = 'healthy'
        movie_count_db = 0
        recommendation_count_db = 0
        
        try:
            movie_count_db = Movie.query.count()
            recommendation_count_db = Recommendation.query.count()
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        status = {
            'status': 'healthy',
            'database_status': db_status,
            'movie_data_loaded': movie_data is not None,
            'similarity_matrix_loaded': similarity_matrix is not None,
            'movies_in_database': movie_count_db,
            'recommendations_in_database': recommendation_count_db
        }
        
        if movie_data is not None:
            status['pickle_movies_count'] = len(movie_data)
        
        if similarity_matrix is not None:
            status['similarity_matrix_shape'] = similarity_matrix.shape
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/movies/<int:movie_id>')
def get_movie_details(movie_id):
    """Get detailed information about a specific movie"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        return jsonify(movie.to_dict())
    except Exception as e:
        app.logger.error(f"Error getting movie details: {str(e)}")
        return jsonify({'error': 'Failed to retrieve movie details'}), 500

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        stats = {
            'total_movies': Movie.query.count(),
            'total_recommendations': Recommendation.query.count(),
            'total_users': User.query.count(),
            'total_ratings': UserRating.query.count(),
            'recommendation_requests': RecommendationHistory.query.count()
        }
        
        # Get most popular movies (most recommended)
        popular_movies = db.session.query(
            Movie.title, 
            db.func.count(Recommendation.id).label('recommendation_count')
        ).join(
            Recommendation, Movie.id == Recommendation.recommended_movie_id
        ).group_by(
            Movie.id, Movie.title
        ).order_by(
            db.func.count(Recommendation.id).desc()
        ).limit(5).all()
        
        stats['most_recommended_movies'] = [
            {'title': title, 'recommendation_count': count} 
            for title, count in popular_movies
        ]
        
        return jsonify(stats)
        
    except Exception as e:
        app.logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
