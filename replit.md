# Movie Recommender System

## Overview

This is a machine learning-powered movie recommendation system built with Flask that provides personalized movie suggestions based on content similarity. The system uses pre-computed similarity matrices derived from movie features to recommend similar films to users based on their selection.

## System Architecture

### Frontend Architecture
- **Framework**: Vanilla JavaScript with Bootstrap 5 for styling
- **Design Pattern**: Single Page Application (SPA) with dynamic content loading
- **UI Components**: 3D animated card-based layout with movie selection dropdown and recommendation grid
- **Styling**: Advanced CSS with 3D transforms, animated movie posters, floating background elements, and immersive dark theme
- **Visual Features**: Generated movie posters, rating stars, shimmer effects, and smooth 3D transitions

### Backend Architecture
- **Framework**: Flask (Python web framework) with SQLAlchemy ORM
- **Database**: PostgreSQL for persistent data storage and user management
- **Pattern**: Database-first architecture with pickle fallback for legacy support
- **API Design**: RESTful endpoints for movies, recommendations, users, and analytics
- **Data Storage**: Database-primary with pickle file fallback for recommendations

## Key Components

### Core Application Files
- `app.py`: Main Flask application with database integration and API endpoints
- `main.py`: Application entry point
- `models.py`: SQLAlchemy database models for movies, users, and recommendations
- `migrate_data.py`: Database migration script for populating data from pickle files
- `templates/index.html`: Single-page frontend interface with 3D movie posters
- `static/js/app.js`: Frontend JavaScript logic for user interactions and visual effects
- `static/css/custom.css`: Advanced 3D styling and animation definitions

### Machine Learning Components
- `movie_list.pkl`: Serialized movie dataset containing movie metadata
- `similarity.pkl`: Pre-computed similarity matrix for content-based filtering
- Content-based recommendation algorithm using cosine similarity

### Alternative Implementation
- `attached_assets/App_1751478649527.py`: Streamlit-based alternative interface (not currently active)

## Data Flow

1. **Initialization**: Application loads pickled movie data and similarity matrix on startup
2. **Movie Selection**: Frontend fetches available movies via `/api/movies` endpoint
3. **User Interaction**: User selects a movie from dropdown interface
4. **Recommendation Request**: Frontend sends selected movie to `/api/recommend` endpoint
5. **Processing**: Backend finds movie index and calculates top 10 similar movies using pre-computed similarity matrix
6. **Response**: System returns ranked list of recommended movies
7. **Display**: Frontend renders recommendations in responsive grid layout

## External Dependencies

### Python Libraries
- **Flask**: Web framework for API and routing
- **Werkzeug**: WSGI utilities and proxy fix middleware
- **Pickle**: Data serialization for model persistence

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library for enhanced UI
- **Custom CSS**: Additional styling for movie-specific theming

### Development Dependencies
- **Streamlit**: Alternative UI framework (in attached assets)
- **Pandas**: Data manipulation (referenced in Streamlit version)

## Deployment Strategy

### Current Setup
- Flask development server configuration
- Environment-based secret key management
- Proxy fix middleware for deployment behind reverse proxies
- Static file serving for CSS/JS assets

### Production Considerations
- Requires WSGI server (Gunicorn, uWSGI) for production deployment
- Environment variables for configuration management
- CDN integration for Bootstrap and Font Awesome resources

## Changelog
- July 02, 2025: Initial setup
- July 02, 2025: Enhanced with 3D visual effects, animated movie posters, rating stars, and immersive UI design
- July 02, 2025: Integrated PostgreSQL database with comprehensive data models for users, movies, ratings, and recommendations

## User Preferences

Preferred communication style: Simple, everyday language.