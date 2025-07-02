# Movie Recommendation System

A sophisticated movie recommendation web application featuring 3D visual effects, machine learning-powered suggestions, and comprehensive database integration.

## Features

- **3D Interactive Interface**: Immersive movie posters with animated effects and smooth transitions
- **Machine Learning Recommendations**: Content-based filtering using cosine similarity
- **Database Integration**: PostgreSQL for persistent storage and user management
- **Rating System**: Star ratings based on similarity scores
- **Analytics**: Comprehensive tracking and recommendation history
- **Responsive Design**: Mobile-friendly Bootstrap interface with dark theme

## Technology Stack

- **Backend**: Flask, SQLAlchemy, PostgreSQL
- **Frontend**: Vanilla JavaScript, Bootstrap 5, Custom CSS with 3D animations
- **Machine Learning**: scikit-learn, pandas, numpy
- **Database**: PostgreSQL with comprehensive data models

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database
- pip or uv package manager

### Installation

1. **Clone or extract the project files**

2. **Install dependencies**:
   ```bash
   pip install flask flask-sqlalchemy gunicorn numpy pandas scikit-learn psycopg2-binary werkzeug email-validator
   ```

3. **Set up environment variables**:
   ```bash
   export DATABASE_URL="postgresql://username:password@host:port/database"
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Initialize the database**:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

5. **Populate with sample data**:
   ```bash
   python create_sample_data.py
   python migrate_data.py
   ```

6. **Run the application**:
   ```bash
   # Development
   python main.py
   
   # Production
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

## Project Structure

```
movie-recommender/
├── app.py                 # Main Flask application
├── main.py                # Application entry point
├── models.py              # Database models
├── migrate_data.py        # Database migration script
├── create_sample_data.py  # Sample data generator
├── movie_list.pkl         # Movie dataset
├── similarity.pkl         # Pre-computed similarity matrix
├── static/
│   ├── css/
│   │   └── custom.css     # 3D styling and animations
│   └── js/
│       └── app.js         # Frontend JavaScript logic
├── templates/
│   └── index.html         # Main HTML template
├── pyproject.toml         # Python dependencies
└── README.md              # This file
```

## Database Models

- **Movies**: Store movie information with genres and descriptions
- **Users**: User authentication and profile management
- **UserRatings**: User ratings and reviews for movies
- **Recommendations**: Pre-computed movie recommendations
- **RecommendationHistory**: Analytics and tracking data
- **SimilarityMatrix**: Stored similarity calculations

## API Endpoints

- `GET /` - Main application interface
- `GET /api/movies` - List all available movies
- `POST /api/recommend` - Get movie recommendations
- `GET /api/health` - System health and status check
- `GET /api/movies/<id>` - Get specific movie details
- `GET /api/stats` - System statistics and analytics

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SESSION_SECRET`: Secret key for session management
- `FLASK_ENV`: Environment (development/production)

### Database Configuration

The application uses PostgreSQL with automatic table creation. Ensure your database is accessible and the connection string is properly configured.

## Development

### Adding New Movies

1. Add movie data to the database using the Movie model
2. Regenerate similarity matrix using `create_sample_data.py`
3. Update recommendations using `migrate_data.py`

### Customizing the Interface

- Modify `static/css/custom.css` for styling changes
- Update `static/js/app.js` for functionality changes
- Edit `templates/index.html` for layout modifications

## Production Deployment

1. Set up a PostgreSQL database
2. Configure environment variables
3. Use a WSGI server like Gunicorn
4. Set up reverse proxy (nginx/Apache) if needed
5. Enable SSL/HTTPS for production use

## Troubleshooting

### Common Issues

1. **Database Connection Error**: Verify DATABASE_URL and PostgreSQL service
2. **Missing Dependencies**: Run `pip install -r requirements.txt` (create from pyproject.toml)
3. **Permission Errors**: Ensure database user has proper permissions
4. **Port Conflicts**: Change port in Gunicorn command if 5000 is occupied

### Logging

The application uses Python's logging module. Check console output for detailed error messages and debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Credits

- Bootstrap for responsive design framework
- Font Awesome for icons
- scikit-learn for machine learning algorithms
- Flask and SQLAlchemy for web framework and ORM

For more detailed information, see `replit.md` in the project root.