#!/usr/bin/env python3
"""
Create sample movie data and similarity matrix for the recommendation system.
This script generates realistic movie data using the same approach as the Jupyter notebook.
"""

import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample movie data with id, title, genre, and overview (matching the notebook structure)
movies_data = [
    {"id": 278, "title": "The Shawshank Redemption", "genre": "Drama,Crime", "overview": "Framed in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison, where he puts his accounting skills to work for an amoral warden."},
    {"id": 238, "title": "The Godfather", "genre": "Drama,Crime", "overview": "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family."},
    {"id": 424, "title": "Schindler's List", "genre": "Drama,History,War", "overview": "The true story of how businessman Oskar Schindler saved over a thousand Jewish lives from the Nazis while they worked as slaves in his factory during World War II."},
    {"id": 240, "title": "The Godfather: Part II", "genre": "Drama,Crime", "overview": "In the continuing saga of the Corleone crime family, a young Vito Corleone grows up in Sicily and in 1910s New York."},
    {"id": 27205, "title": "Inception", "genre": "Action,Thriller,Science Fiction,Mystery,Adventure", "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life as payment for a task considered to be impossible: inception."},
    {"id": 603, "title": "The Matrix", "genre": "Action,Science Fiction", "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth."},
    {"id": 13, "title": "Forrest Gump", "genre": "Comedy,Drama,Romance", "overview": "A man with a low IQ has accomplished great things in his life and been present during significant historic events—in each case, far exceeding what anyone imagined he could do."},
    {"id": 769, "title": "GoodFellas", "genre": "Drama,Crime", "overview": "The true story of Henry Hill, a half-Irish, half-Sicilian Brooklyn kid who is adopted by neighbourhood gangsters at an early age and climbs the ranks of a Mafia family under the guidance of Jimmy Conway."},
    {"id": 550, "title": "Fight Club", "genre": "Drama", "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy."},
    {"id": 120, "title": "The Lord of the Rings: The Fellowship of the Ring", "genre": "Adventure,Fantasy,Action", "overview": "Young hobbit Frodo Baggins, after inheriting a mysterious ring from his uncle Bilbo, must leave his home in order to keep it from falling into the hands of its evil creator."},
    {"id": 11, "title": "Star Wars", "genre": "Adventure,Action,Science Fiction", "overview": "Princess Leia is captured and held hostage by the evil Imperial forces in their effort to take over the galactic Empire."},
    {"id": 289, "title": "Casablanca", "genre": "Drama,Romance", "overview": "In Casablanca, Morocco in December 1941, a cynical American expatriate meets a former lover, with unforeseen complications."},
    {"id": 274, "title": "The Silence of the Lambs", "genre": "Crime,Drama,Thriller", "overview": "Clarice Starling is a top student at the FBI's training academy. Jack Crawford wants Clarice to interview Dr. Hannibal Lecter, a brilliant psychiatrist who is also a violent psychopath."},
    {"id": 857, "title": "Saving Private Ryan", "genre": "Drama,History,War", "overview": "As U.S. troops storm the beaches of Normandy, three brothers lie dead on the battlefield, with a fourth trapped behind enemy lines."},
    {"id": 597, "title": "Titanic", "genre": "Drama,Romance", "overview": "101-year-old Rose DeWitt Bukater tells the story of her life aboard the Titanic, 84 years later."},
    {"id": 24428, "title": "The Avengers", "genre": "Science Fiction,Action,Adventure", "overview": "When an unexpected enemy emerges and threatens global safety and security, Nick Fury, director of the international peacekeeping agency known as S.H.I.E.L.D., finds himself in need of a team to pull the world back from the brink of disaster."},
    {"id": 329, "title": "Jurassic Park", "genre": "Adventure,Science Fiction", "overview": "A wealthy entrepreneur secretly creates a theme park featuring living dinosaurs drawn from prehistoric DNA."},
    {"id": 218, "title": "The Terminator", "genre": "Action,Thriller,Science Fiction", "overview": "In the post-apocalyptic future, reigning tyrannical supercomputers teleport a cyborg assassin known as the Terminator back to 1984 to kill Sarah Connor."},
    {"id": 105, "title": "Back to the Future", "genre": "Adventure,Comedy,Science Fiction", "overview": "Eighties teenager Marty McFly is accidentally sent back in time to 1955, inadvertently disrupting his parents' first meeting."},
    {"id": 85, "title": "Raiders of the Lost Ark", "genre": "Action,Adventure", "overview": "When Dr. Indiana Jones – the tweed-suited professor who just happens to be a celebrated archaeologist – is hired by the government to locate the legendary Ark of the Covenant."},
    {"id": 601, "title": "E.T. the Extra-Terrestrial", "genre": "Science Fiction,Adventure,Family,Fantasy", "overview": "An alien is left behind on Earth and saved by the 10-year-old Elliot who decides to keep him hidden in his home."},
    {"id": 8587, "title": "The Lion King", "genre": "Family,Animation,Drama", "overview": "A young lion cub named Simba can't wait to be king. But his uncle craves the title for himself and will stop at nothing to get it."},
    {"id": 862, "title": "Toy Story", "genre": "Animation,Comedy,Family", "overview": "Led by Woody, Andy's toys live happily in his room until Andy's birthday brings Buzz Lightyear onto the scene."},
    {"id": 12, "title": "Finding Nemo", "genre": "Animation,Family,Comedy", "overview": "Nemo, an adventurous young clownfish, is unexpectedly taken from his Great Barrier Reef home to a dentist's office aquarium."},
    {"id": 9806, "title": "The Incredibles", "genre": "Action,Adventure,Animation,Family", "overview": "Bob Parr has given up his superhero days to log in time as an insurance adjuster and raise his three children with his formerly heroic wife in suburbia."},
    {"id": 98, "title": "Gladiator", "genre": "Action,Drama,Adventure", "overview": "In the year 180, the death of emperor Marcus Aurelius throws the Roman Empire into chaos."},
    {"id": 197, "title": "Braveheart", "genre": "Action,Drama,History,War", "overview": "Enraged at the slaughter of Murron, his new bride and childhood love, Scottish warrior William Wallace slays a platoon of the local English lord's soldiers."},
    {"id": 497, "title": "The Green Mile", "genre": "Fantasy,Drama,Crime", "overview": "A supernatural tale set on death row in a Southern prison, where gentle giant John Coffey possesses the mysterious power to heal people's ailments."},
    {"id": 19995, "title": "Avatar", "genre": "Action,Adventure,Fantasy,Science Fiction", "overview": "In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission."},
    {"id": 155, "title": "The Dark Knight", "genre": "Drama,Action,Crime,Thriller", "overview": "Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and District Attorney Harvey Dent."}
]

def create_movie_dataset():
    """Create a pandas DataFrame with movie data following the notebook approach"""
    print("Creating movie dataset...")
    
    # Create DataFrame
    df = pd.DataFrame(movies_data)
    
    # Combine genre and overview to create tags (same as notebook approach)
    df['tags'] = df['genre'] + df['overview']
    
    # Keep only the columns we need (id, title, tags)
    df = df[['id', 'title', 'tags']]
    
    print(f"Created dataset with {len(df)} movies")
    return df

def calculate_similarity_matrix(df):
    """Calculate content-based similarity matrix using CountVectorizer (same as notebook)"""
    print("Calculating similarity matrix...")
    
    # Use CountVectorizer with same parameters as notebook
    cv = CountVectorizer(max_features=10000, stop_words='english')
    vector = cv.fit_transform(df['tags'].astype('U')).toarray()
    
    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(vector)
    
    print(f"Created similarity matrix with shape: {similarity_matrix.shape}")
    return similarity_matrix

def save_pickle_files(df, similarity_matrix):
    """Save the DataFrame and similarity matrix as pickle files"""
    print("Saving pickle files...")
    
    # Save movie data
    with open('movie_list.pkl', 'wb') as f:
        pickle.dump(df, f)
    print("Saved movie_list.pkl")
    
    # Save similarity matrix
    with open('similarity.pkl', 'wb') as f:
        pickle.dump(similarity_matrix, f)
    print("Saved similarity.pkl")

def main():
    """Main function to create and save movie recommendation data"""
    print("=== Movie Recommendation Data Generator ===")
    
    # Create movie dataset
    movie_df = create_movie_dataset()
    
    # Calculate similarity matrix
    similarity = calculate_similarity_matrix(movie_df)
    
    # Save to pickle files
    save_pickle_files(movie_df, similarity)
    
    print("\n=== Data Generation Complete ===")
    print(f"Generated {len(movie_df)} movies with similarity calculations")
    print("Files created:")
    print("- movie_list.pkl (movie dataset)")
    print("- similarity.pkl (similarity matrix)")
    print("\nThe Flask app should now work properly!")

if __name__ == "__main__":
    main()