import requests
import threading
from io import BytesIO
from PIL import Image
from collections import Counter
import config

TMDB_API_KEY = "d758564ccd7127ab4e0e38901e85d76a"
OMDB_API_KEY = "d8257053" 
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def fetch_movie_metadata(title, year):
    try:
        omdb_url = f"http://www.omdbapi.com/?t={title}&y={year}&apikey={OMDB_API_KEY}"
        omdb_data = requests.get(omdb_url).json()
        if omdb_data.get('Response') == 'False': return None
        tmdb_search = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}&primary_release_year={year}"
        tmdb_res = requests.get(tmdb_search).json()
        poster_img, trailer_url = None, None
        if tmdb_res.get('results'):
            movie = tmdb_res['results'][0]
            if movie.get('poster_path'):
                img_res = requests.get(IMAGE_BASE_URL + movie['poster_path'])
                poster_img = Image.open(BytesIO(img_res.content))
            v_res = requests.get(f"https://api.themoviedb.org/3/movie/{movie['id']}/videos?api_key={TMDB_API_KEY}").json()
            yt_key = next((v['key'] for v in v_res.get('results', []) if v['site'] == 'YouTube' and v['type'] == 'Trailer'), None)
            if yt_key: trailer_url = f"https://www.youtube.com/watch?v={yt_key}"
        return {"omdb": omdb_data, "poster": poster_img, "trailer": trailer_url}
    except: return None

def load_movie_details(title, year, vars_dict, callbacks):
    def task():
        data = fetch_movie_metadata(title, year)
        if data:
            omdb = data['omdb']
            vars_dict['genre'].set(omdb.get('Genre', 'N/A'))
            vars_dict['director'].set(omdb.get('Director', 'N/A'))
            vars_dict['duration'].set(omdb.get('Runtime', 'N/A'))
            vars_dict['rating'].set(omdb.get('imdbRating', 'N/A'))
            vars_dict['language'].set(omdb.get('Language', 'N/A'))
            callbacks['on_trailer_load'](data['trailer'])
            if data['poster']: callbacks['on_poster_load'](data['poster'])
        else:
            for var in vars_dict.values(): var.set("N/A")
    threading.Thread(target=task, daemon=True).start()

def get_movie_stats(current_user_id, database_module):
    conn = database_module.create_connection()
    data = conn.execute("SELECT genre, status FROM movies WHERE user_id=?", (current_user_id,)).fetchall()
    conn.close()
    status_list = [m['status'] for m in data if m['status']]
    no_status_count = sum(1 for m in data if not m['status'])
    genres = []
    for m in data:
        if m['genre']: genres.extend([g.strip() for g in m['genre'].split(',')])
    fav_genre = Counter(genres).most_common(1)[0][0] if genres else "N/A"
    return {"total": len(data), "fav_genre": fav_genre, "status_counts": Counter(status_list), "no_status": no_status_count, "raw_data": data}

def get_similar_movies(movie_title):
    try:
        clean_title = movie_title.split('(')[0].strip() 
        
        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": config.TMDB_API_KEY,
            "query": clean_title
        }
        
        response = requests.get(search_url, params=params).json()
        
        if not response.get('results'): 
            return []

        movie_id = response['results'][0]['id']
        
        rec_url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations"
        rec_params = {"api_key": config.TMDB_API_KEY}
        
        rec_data = requests.get(rec_url, params=rec_params).json()
        return rec_data.get('results', [])[:30] 
        
    except Exception as e:
        print(f"API Error: {e}")
        return []