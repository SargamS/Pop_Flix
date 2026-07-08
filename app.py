import requests
import streamlit as st
import base64

# ==== Streamlit Page Config ====
st.set_page_config(page_title="PopFlix", layout="wide")

# ==== Function to Convert Logo to Base64 ====
def get_base64_img(image_path):
    with open(image_path, "rb") as img_file:
        data = img_file.read()
        return base64.b64encode(data).decode()

# ==== Load and Encode Logo ====
logo_base64 = get_base64_img("logo.png")

# ==== Header with Logo and Title ====
st.markdown(f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-top: 10px;">
        <img src="data:image/png;base64,{logo_base64}" style="height: 90px; margin-right: 10px;"/>
        <h1 style="font-size: 64px; margin: 0;">PopFlix</h1>
    </div>
""", unsafe_allow_html=True)

# ==== Tagline ====
st.markdown("""
    <p style='text-align: center; font-size: 24px; margin-top: 10px;'>
        Because scrolling for 45 minutes is a real horror movie.
    </p>
    <p style='text-align: center; font-size: 20px;'>
        Type any movie you love — and PopFlix will suggest five similar films, complete with posters and titles.
    </p>
""", unsafe_allow_html=True)

# ==== Dark Mode Toggle ====
dark_mode = st.toggle("🌙 Dark Mode", value=True)
bg_color = "#111" if dark_mode else "#fff"
text_color = "#fff" if dark_mode else "#000"

# ==== Custom CSS Styling ====
st.markdown(f"""
    <style>
        .movie-card {{
            display: inline-block;
            margin: 10px;
            text-align: center;
            background-color: {bg_color};
            color: {text_color};
            padding: 10px;
            border-radius: 12px;
            width: 200px;
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        .movie-card:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
        }}
        .movie-poster {{
            width: 100%;
            border-radius: 8px;
        }}
        .movie-title {{
            font-size: 18px;
            font-weight: bold;
            margin-top: 10px;
        }}
        .movie-subtext {{
            font-size: 16px;
            margin-top: 6px;
        }}
        .trailer-button {{
            margin-top: 10px;
            display: inline-block;
            padding: 8px 14px;
            border-radius: 6px;
            background-color: #e50914;
            color: white;
            text-decoration: none;
            font-size: 16px;
            font-weight: bold;
        }}
        .hero-card {{
            display: flex;
            gap: 24px;
            align-items: flex-start;
            background-color: {bg_color};
            color: {text_color};
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 30px;
        }}
        .hero-poster {{
            width: 220px;
            border-radius: 12px;
            flex-shrink: 0;
        }}
        .hero-title {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .hero-subtext {{
            font-size: 18px;
            margin-top: 6px;
        }}
    </style>
""", unsafe_allow_html=True)

# ==== TMDB API Fetch ====
TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"

def fetch_movie_metadata(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url, timeout=8).json()
        poster_path = data.get('poster_path')
        imdb_rating = data.get('vote_average', 'N/A')
        overview = data.get('overview', '')
        genres = ", ".join([genre['name'] for genre in data.get('genres', [])])
        trailer_url = f"https://www.youtube.com/results?search_query={'+'.join(data.get('title', '').split())}+trailer"
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
        return poster_url, imdb_rating, genres, trailer_url, overview
    except Exception:
        return "https://via.placeholder.com/500x750?text=Error", "N/A", "", "#", ""

# ==== Search TMDB for Any Movie in the World ====
@st.cache_data(show_spinner=False)
def search_movies(query):
    try:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&language=en-US&query={requests.utils.quote(query)}"
        data = requests.get(url, timeout=8).json()
        results = []
        for r in data.get('results', [])[:8]:
            year = (r.get('release_date') or '')[:4]
            label = f"{r['title']} ({year})" if year else r['title']
            results.append({"id": r['id'], "label": label})
        return results
    except Exception:
        return []

# ==== Get Recommendations for a Given Movie ID ====
def recommend(movie_id):
    results = []
    for endpoint in ["recommendations", "similar"]:
        try:
            url = f"https://api.themoviedb.org/3/movie/{movie_id}/{endpoint}?api_key={TMDB_API_KEY}&language=en-US"
            data = requests.get(url, timeout=8).json()
            candidates = data.get('results', [])
            if candidates:
                for r in candidates[:5]:
                    poster, rating, genres, trailer, _ = fetch_movie_metadata(r['id'])
                    results.append((r['title'], poster, rating, genres, trailer))
                if results:
                    break
        except Exception:
            continue
    return results

# ==== Free-Text Movie Search (Any Movie, Powered by TMDB) ====
st.markdown("<h3 style='font-size: 26px;'>🎥 Type any movie in the world:</h3>", unsafe_allow_html=True)
query = st.text_input("", placeholder="e.g. Inception, The Dark Knight, Titanic...")

selected_id = None
selected_label = None

if query:
    with st.spinner("Searching..."):
        matches = search_movies(query)
    if not matches:
        st.warning(f"No movie found matching \"{query}\". Try a different spelling or another title.")
    elif len(matches) == 1:
        selected_id = matches[0]['id']
        selected_label = matches[0]['label']
    else:
        options = {m['label']: m['id'] for m in matches}
        chosen_label = st.selectbox("Did you mean:", list(options.keys()))
        selected_id = options[chosen_label]
        selected_label = chosen_label

if selected_id:
    if st.button("✨ Recommend"):
        # ---- Hero card for the searched movie ----
        poster, rating, genres, trailer, overview = fetch_movie_metadata(selected_id)

        st.markdown(f"""
            <div class="hero-card">
                <img src="{poster}" class="hero-poster" />
                <div>
                    <div class="hero-title">{selected_label}</div>
                    <div class="hero-subtext">⭐ IMDb: {rating}</div>
                    <div class="hero-subtext">🎭 {genres}</div>
                    <div class="hero-subtext">{overview}</div>
                    <a class="trailer-button" href="{trailer}" target="_blank">▶ Watch Trailer</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # ---- Recommendations below ----
        with st.spinner("Finding similar movies..."):
            results = recommend(selected_id)

        st.subheader("💡 You may also like:")

        if not results:
            st.info("No recommendations available for this movie yet.")
        else:
            cols = st.columns(len(results))
            for i in range(len(results)):
                with cols[i]:
                    st.markdown(f"""
                        <div class="movie-card">
                            <img src="{results[i][1]}" class="movie-poster" />
                            <div class="movie-title">{results[i][0]}</div>
                            <div class="movie-subtext">⭐ IMDb: {results[i][2]}</div>
                            <div class="movie-subtext">🎭 {results[i][3]}</div>
                            <a class="trailer-button" href="{results[i][4]}" target="_blank">▶ Watch Trailer</a>
                        </div>
                    """, unsafe_allow_html=True)
