import os
from pathlib import Path
import sqlite3

APP_NAME = "CineTrack"

# Create application data directory in APPDATA
app_data = Path(os.getenv('APPDATA')) / APP_NAME
app_data.mkdir(parents=True, exist_ok=True)

# Database file path
DB_FILE = app_data / ".syscache"

# Create a new SQLite database connection with optimized PRAGMA settings.
def create_connection():
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  
        conn.execute("PRAGMA foreign_keys = 1")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA secure_delete = 1")

        return conn                     
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

# Create required tables ('users', 'movies') if they do not exist.
def initialize_database():
    conn = create_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            username TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL,
            profile_path TEXT DEFAULT ''
        )""")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER NOT NULL, 
            title TEXT, 
            genre TEXT, 
            director TEXT, 
            release_year TEXT, 
            duration TEXT, 
            rating TEXT, 
            language TEXT, 
            status TEXT, 
            remarks TEXT, 
            FOREIGN KEY (user_id) REFERENCES users (id)
        )""")

    conn.commit()
    conn.close()

# Retrieve the profile image path for a given user.
def get_user_profile_path(user_id):
    conn = create_connection()
    user = conn.execute("SELECT profile_path FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user['profile_path'] if user else None

# Update the file path of the user's profile picture.
def update_profile_path(user_id, path):
    conn = create_connection()
    conn.execute("UPDATE users SET profile_path = ? WHERE id = ?", (path, user_id))
    conn.commit()
    conn.close()

# Securely update a user's username.
def update_username_secure(user_id, current_pass, new_username):
    conn = create_connection()
    try:
        user = conn.execute("SELECT password FROM users WHERE id=?", (user_id,)).fetchone()
        
        if not user or user['password'] != current_pass:
            return False, "Current password incorrect."

        conn.execute("UPDATE users SET username=? WHERE id=?", (new_username, user_id))
        conn.commit()
        return True, "Success"
        
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Securely update a user's password.
def update_password_secure(user_id, current_pass, new_pass):
    conn = create_connection()
    try:
        user = conn.execute("SELECT password FROM users WHERE id=?", (user_id,)).fetchone()
        
        if not user or user['password'] != current_pass:
            return False, "The current password you entered is incorrect."

        conn.execute("UPDATE users SET password=? WHERE id=?", (new_pass, user_id))
        conn.commit()
        return True, "Success"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Clear a user's profile image path in the database.
def clear_user_profile_path(user_id):
    conn = create_connection()
    conn.execute("UPDATE users SET profile_path = '' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# Insert a new movie record associated with a user.
def add_movie_to_db(user_id, title, genre, director, year, duration, rating, language, status, remarks):
    conn = create_connection()
    query = """INSERT INTO movies (user_id, title, genre, director, release_year, 
            duration, rating, language, status, remarks) VALUES (?,?,?,?,?,?,?,?,?,?)"""
    conn.execute(query, (user_id, title, genre, director, year, duration, rating, language, status, remarks))
    conn.commit()
    conn.close()

# Update an existing movie record by its ID.
def update_movie_in_db(movie_id, title, genre, director, year, duration, rating, language, status, remarks):
    conn = create_connection()
    query = """UPDATE movies SET title=?, genre=?, director=?, release_year=?, 
               duration=?, rating=?, language=?, status=?, remarks=? WHERE id=?"""
    conn.execute(query, (title, genre, director, year, duration, rating, language, status, remarks, movie_id))
    conn.commit()
    conn.close()

# Delete a movie record by its ID.
def delete_movie_from_db(movie_id):
    conn = create_connection()
    conn.execute("DELETE FROM movies WHERE id=?", (movie_id,))
    conn.commit()
    conn.close()

# Returns a list of matching rows.
def search_movies(user_id, search_val):
    conn = create_connection()
    s = f'%{search_val.lower()}%'
    q = """
        SELECT id, title, genre, director, release_year, duration, rating, language, status, remarks 
        FROM movies 
        WHERE user_id=? AND (
            LOWER(title) LIKE ? OR LOWER(genre) LIKE ? OR LOWER(director) LIKE ? OR 
            LOWER(language) LIKE ? OR LOWER(status) LIKE ? OR LOWER(remarks) LIKE ? OR 
            CAST(release_year AS TEXT) LIKE ? OR CAST(rating AS TEXT) LIKE ? OR 
            CAST(duration AS TEXT) LIKE ?
        )
    """
    cursor = conn.execute(q, (user_id, s, s, s, s, s, s, s, s, s))
    results = cursor.fetchall()
    conn.close()
    return results

# Verify user credentials for login.
def verify_user_login(username, password):
    conn = create_connection()
    user = conn.execute(
        "SELECT id, username FROM users WHERE username=? AND password=?", 
        (username, password)
    ).fetchone()
    conn.close()
    return user 

# Retrieve a simplified list of movies for CSV or PDF export.
def get_movies_for_export(user_id):
    conn = create_connection()
    movies = conn.execute(
        "SELECT title, genre, release_year, status FROM movies WHERE user_id = ?", 
        (user_id,)
    ).fetchall()
    conn.close()
    return movies

# Register a new user in the database.
def register_user(username, password):
    conn = create_connection()
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True, "Success"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another one."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# Fetch all movies for a user, sorted alphabetically by title.
def get_user_movies(user_id):
    conn = create_connection()
    query = """
        SELECT id, title, genre, director, release_year, 
               duration, rating, language, status, remarks 
        FROM movies 
        WHERE user_id=? 
        ORDER BY title ASC
    """
    rows = conn.execute(query, (user_id,)).fetchall()
    conn.close()
    return rows