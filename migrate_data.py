#!/usr/bin/env python3
"""
Database migration script to populate the movie database with data from pickle files
"""

import pickle
import logging
from datetime import datetime
from app import app, db
from models import Movie, Recommendation, SimilarityMatrix
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_pickle_data():
    """Load movie data and similarity matrix from pickle files"""
    try:
        # Load movie data
        with open('movie_list.pkl', 'rb') as f:
            movie_data = pickle.load(f)
        logger.info(f"Loaded {len(movie_data)} movies from pickle file")
        
        # Load similarity matrix
        with open('similarity.pkl', 'rb') as f:
            similarity_matrix = pickle.load(f)
        logger.info(f"Loaded similarity matrix with shape: {similarity_matrix.shape}")
        
        return movie_data, similarity_matrix
        
    except Exception as e:
        logger.error(f"Error loading pickle files: {str(e)}")
        return None, None

def migrate_movies(movie_data):
    """Migrate movie data to the database"""
    logger.info("Starting movie data migration...")
    
    migrated_count = 0
    skipped_count = 0
    
    for index, row in movie_data.iterrows():
        try:
            # Check if movie already exists
            existing_movie = Movie.query.filter_by(title=row['title']).first()
            if existing_movie:
                skipped_count += 1
                continue
            
            # Create new movie record
            movie = Movie(
                tmdb_id=row.get('id', None),
                title=row['title'],
                genre=row.get('genre', ''),
                overview=row.get('overview', ''),
                tags=row['tags'],
                created_at=datetime.utcnow()
            )
            
            db.session.add(movie)
            migrated_count += 1
            
            # Commit in batches to avoid memory issues
            if migrated_count % 50 == 0:
                db.session.commit()
                logger.info(f"Migrated {migrated_count} movies so far...")
                
        except Exception as e:
            logger.error(f"Error migrating movie '{row['title']}': {str(e)}")
            db.session.rollback()
            continue
    
    # Final commit
    try:
        db.session.commit()
        logger.info(f"Movie migration completed: {migrated_count} migrated, {skipped_count} skipped")
        return True
    except Exception as e:
        logger.error(f"Error committing movie data: {str(e)}")
        db.session.rollback()
        return False

def migrate_similarity_data(movie_data, similarity_matrix):
    """Migrate similarity data to create recommendations"""
    logger.info("Starting similarity data migration...")
    
    movies = Movie.query.all()
    movie_id_map = {movie.title: movie.id for movie in movies}
    
    recommendation_count = 0
    
    for i, row in movie_data.iterrows():
        try:
            source_title = row['title']
            source_movie_id = movie_id_map.get(source_title)
            
            if not source_movie_id:
                continue
            
            # Get similarity scores for this movie
            similarity_scores = list(enumerate(similarity_matrix[i]))
            similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
            
            # Create top 10 recommendations (excluding the movie itself)
            for rank, (target_index, score) in enumerate(similarity_scores[1:11], 1):
                try:
                    target_title = movie_data.iloc[target_index]['title']
                    target_movie_id = movie_id_map.get(target_title)
                    
                    if not target_movie_id:
                        continue
                    
                    # Check if recommendation already exists
                    existing_rec = Recommendation.query.filter_by(
                        source_movie_id=source_movie_id,
                        recommended_movie_id=target_movie_id
                    ).first()
                    
                    if existing_rec:
                        continue
                    
                    # Create recommendation
                    recommendation = Recommendation(
                        source_movie_id=source_movie_id,
                        recommended_movie_id=target_movie_id,
                        similarity_score=float(score),
                        rank=rank,
                        created_at=datetime.utcnow()
                    )
                    
                    db.session.add(recommendation)
                    recommendation_count += 1
                    
                except Exception as e:
                    logger.error(f"Error creating recommendation for {source_title}: {str(e)}")
                    continue
            
            # Commit in batches
            if recommendation_count % 100 == 0:
                db.session.commit()
                logger.info(f"Created {recommendation_count} recommendations so far...")
                
        except Exception as e:
            logger.error(f"Error processing movie {source_title}: {str(e)}")
            continue
    
    # Final commit
    try:
        db.session.commit()
        logger.info(f"Similarity data migration completed: {recommendation_count} recommendations created")
        return True
    except Exception as e:
        logger.error(f"Error committing similarity data: {str(e)}")
        db.session.rollback()
        return False

def migrate_similarity_matrix(movie_data, similarity_matrix):
    """Store the similarity matrix in the database for future use"""
    logger.info("Starting similarity matrix migration...")
    
    movies = Movie.query.all()
    movie_id_map = {movie.title: movie.id for movie in movies}
    
    matrix_count = 0
    
    for i, row1 in movie_data.iterrows():
        for j, row2 in movie_data.iterrows():
            if i >= j:  # Avoid duplicates and self-similarity
                continue
            
            try:
                movie1_id = movie_id_map.get(row1['title'])
                movie2_id = movie_id_map.get(row2['title'])
                
                if not movie1_id or not movie2_id:
                    continue
                
                # Check if similarity already exists
                existing_sim = SimilarityMatrix.query.filter_by(
                    movie1_id=movie1_id,
                    movie2_id=movie2_id
                ).first()
                
                if existing_sim:
                    continue
                
                similarity_score = float(similarity_matrix[i][j])
                
                # Only store significant similarities to save space
                if similarity_score > 0.01:
                    sim_record = SimilarityMatrix(
                        movie1_id=movie1_id,
                        movie2_id=movie2_id,
                        similarity_score=similarity_score,
                        algorithm='cosine_similarity',
                        created_at=datetime.utcnow()
                    )
                    
                    db.session.add(sim_record)
                    matrix_count += 1
                
                # Commit in batches
                if matrix_count % 200 == 0:
                    db.session.commit()
                    logger.info(f"Stored {matrix_count} similarity pairs so far...")
                    
            except Exception as e:
                logger.error(f"Error storing similarity between {row1['title']} and {row2['title']}: {str(e)}")
                continue
    
    # Final commit
    try:
        db.session.commit()
        logger.info(f"Similarity matrix migration completed: {matrix_count} pairs stored")
        return True
    except Exception as e:
        logger.error(f"Error committing similarity matrix: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Main migration function"""
    logger.info("=== Starting Database Migration ===")
    
    with app.app_context():
        # Load pickle data
        movie_data, similarity_matrix = load_pickle_data()
        if movie_data is None or similarity_matrix is None:
            logger.error("Failed to load pickle data. Exiting migration.")
            return False
        
        # Ensure database tables exist
        try:
            db.create_all()
            logger.info("Database tables verified/created")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            return False
        
        # Migrate movies
        if not migrate_movies(movie_data):
            logger.error("Movie migration failed. Exiting.")
            return False
        
        # Migrate recommendations
        if not migrate_similarity_data(movie_data, similarity_matrix):
            logger.error("Recommendation migration failed. Continuing...")
        
        # Migrate similarity matrix (optional, for advanced features)
        if not migrate_similarity_matrix(movie_data, similarity_matrix):
            logger.error("Similarity matrix migration failed. Continuing...")
        
        # Print summary
        movie_count = Movie.query.count()
        recommendation_count = Recommendation.query.count()
        similarity_count = SimilarityMatrix.query.count()
        
        logger.info("=== Migration Summary ===")
        logger.info(f"Movies in database: {movie_count}")
        logger.info(f"Recommendations in database: {recommendation_count}")
        logger.info(f"Similarity pairs in database: {similarity_count}")
        logger.info("=== Migration Completed Successfully ===")
        
        return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)