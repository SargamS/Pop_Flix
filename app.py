import requests
import streamlit as st
import base64

# ==== Streamlit Page Config ====
st.set_page_config(page_title="PopFlix", layout="wide", initial_sidebar_state="expanded")

TMDB_API_KEY = "8265bd1679663a7ea12ac168da84d2e8"
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Image"

# ==== Helpers ====
def get_base64_img(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = get_base64_img("logo.png")

# ==== Session State ====
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []  # list of (id, media_type)

# ==== Handle link-driven actions (add/remove list, jump to a movie) ====
params = st.query_params
if "action" in params:
    action = params.get("action")
    mid = params.get("id")
    mtype = params.get("type", "movie")
    if action == "add" and mid:
        entry = (mid, mtype)
        if entry not in st.session_state.watchlist:
            st.session_state.watchlist.append(entry)
    elif action == "remove" and mid:
        st.session_state.watchlist = [w for w in st.session_state.watchlist if w[0] != mid]
    elif action == "view" and mid:
        st.session_state.page = "Movies" if mtype == "movie" else "TV Shows"
        st.session_state.jump_id = mid
        st.session_state.jump_label = params.get("label", "")
    st.query_params.clear()
    st.rerun()

# ==== TMDB Fetchers ====
@st.cache_data(show_spinner=False)
def fetch_genre_map(media_type="movie"):
    try:
        url = f"https://api.themoviedb.org/3/genre/{media_type}/list?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url, timeout=8).json()
        return {g["id"]: g["name"] for g in data.get("genres", [])}
    except Exception:
        return {}

@st.cache_data(show_spinner=False)
def fetch_trending(media_type="movie", n=8):
    try:
        url = f"https://api.themoviedb.org/3/trending/{media_type}/day?api_key={TMDB_API_KEY}"
        data = requests.get(url, timeout=8).json()
        return data.get("results", [])[:n]
    except Exception:
        return []

@st.cache_data(show_spinner=False)
def fetch_now_playing(n=12):
    try:
        url = f"https://api.themoviedb.org/3/movie/now_playing?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url, timeout=8).json()
        return data.get("results", [])[:n]
    except Exception:
        return []

def fetch_metadata(item_id, media_type="movie"):
    try:
        url = f"https://api.themoviedb.org/3/{media_type}/{item_id}?api_key={TMDB_API_KEY}&language=en-US"
        data = requests.get(url, timeout=8).json()
        title = data.get("title") or data.get("name", "")
        poster = data.get("poster_path")
        rating = data.get("vote_average", "N/A")
        genres = ", ".join(g["name"] for g in data.get("genres", []))
        overview = data.get("overview", "")
        trailer = f"https://www.youtube.com/results?search_query={'+'.join(title.split())}+trailer"
        poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else PLACEHOLDER
        return title, poster_url, rating, genres, trailer, overview
    except Exception:
        return "", PLACEHOLDER, "N/A", "", "#", ""

@st.cache_data(show_spinner=False)
def search_titles(query, media_type="movie"):
    try:
        url = f"https://api.themoviedb.org/3/search/{media_type}?api_key={TMDB_API_KEY}&language=en-US&query={requests.utils.quote(query)}"
        data = requests.get(url, timeout=8).json()
        results = []
        for r in data.get("results", [])[:8]:
            name = r.get("title") or r.get("name", "")
            date = (r.get("release_date") or r.get("first_air_date") or "")[:4]
            label = f"{name} ({date})" if date else name
            results.append({"id": r["id"], "label": label})
        return results
    except Exception:
        return []

def recommend(item_id, media_type="movie"):
    results = []
    for endpoint in ["recommendations", "similar"]:
        try:
            url = f"https://api.themoviedb.org/3/{media_type}/{item_id}/{endpoint}?api_key={TMDB_API_KEY}&language=en-US"
            data = requests.get(url, timeout=8).json()
            candidates = data.get("results", [])
            if candidates:
                for r in candidates[:5]:
                    title, poster, rating, genres, trailer, _ = fetch_metadata(r["id"], media_type)
                    results.append({"id": r["id"], "title": title, "poster": poster, "rating": rating,
                                     "genres": genres, "trailer": trailer})
                if results:
                    break
        except Exception:
            continue
    return results

# ==== Global CSS: Netflix-dark theme ====
st.markdown(f"""
<style>
    .stApp {{
        background-color: #0a0a0a;
        color: #eaeaea;
    }}
    header[data-testid="stHeader"] {{ background: transparent; }}
    section[data-testid="stSidebar"] {{
        background-color: #060606;
        border-right: 1px solid #1f1f1f;
    }}
    section[data-testid="stSidebar"] .stButton button {{
        background: none;
        border: none;
        color: #b3b3b3;
        text-align: left;
        width: 100%;
        letter-spacing: 1px;
        font-size: 14px;
        font-weight: 600;
        padding: 10px 4px;
    }}
    section[data-testid="stSidebar"] .stButton button:hover {{
        color: #ffffff;
    }}
    .nav-active button {{
        color: #ffffff !important;
        border-left: 3px solid #e50914 !important;
        padding-left: 10px !important;
    }}
    .topbar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 10px 20px 10px;
        border-bottom: 1px solid #1f1f1f;
        margin-bottom: 25px;
    }}
    .brand {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 0 auto;
    }}
    .brand h1 {{
        color: #e50914;
        font-size: 34px;
        letter-spacing: 2px;
        margin: 0;
    }}
    .profile {{
        display: flex;
        align-items: center;
        gap: 8px;
        color: #d4d4d4;
        font-size: 14px;
        white-space: nowrap;
    }}
    .profile-avatar {{
        width: 30px; height: 30px; border-radius: 50%;
        background: #333; display: flex; align-items: center; justify-content: center;
        font-size: 15px;
    }}
    .tagline {{
        text-align: center; color: #9a9a9a; margin-top: -12px; margin-bottom: 25px; font-size: 15px;
    }}

    /* ---- Fan / accordion hero gallery ---- */
    .fan {{
        display: flex;
        height: 340px;
        gap: 4px;
        margin-bottom: 40px;
        overflow: hidden;
        border-radius: 10px;
    }}
    .fan-item {{
        position: relative;
        flex: 1;
        min-width: 60px;
        border-radius: 8px;
        overflow: hidden;
        background-size: cover;
        background-position: center top;
        transition: flex 0.45s ease;
        cursor: pointer;
    }}
    .fan-item:hover {{ flex: 4; }}
    .fan-item a {{ display: block; width: 100%; height: 100%; text-decoration: none; }}
    .fan-overlay {{
        position: absolute; bottom: 0; left: 0; right: 0;
        padding: 14px 10px;
        background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0));
        color: #fff; font-weight: 700; font-size: 14px; text-align: center;
    }}

    /* ---- Movie / TV cards ---- */
    .movie-card {{
        display: inline-block;
        margin: 8px;
        text-align: center;
        background-color: #141414;
        color: #eaeaea;
        padding: 10px;
        border-radius: 10px;
        width: 100%;
        border: 1px solid #232323;
        transition: transform 0.25s, box-shadow 0.25s;
    }}
    .movie-card:hover {{
        transform: scale(1.03);
        box-shadow: 0 10px 22px rgba(0,0,0,0.55);
        border-color: #e50914;
    }}
    .movie-poster {{ width: 100%; border-radius: 8px; }}
    .movie-title {{ font-size: 16px; font-weight: 700; margin-top: 10px; min-height: 42px; }}
    .movie-subtext {{ font-size: 13px; margin-top: 4px; color: #b3b3b3; }}
    .btn-row {{ display: flex; gap: 6px; justify-content: center; margin-top: 10px; flex-wrap: wrap; }}
    .pill-btn {{
        display: inline-block; padding: 6px 12px; border-radius: 6px;
        background-color: #e50914; color: white !important; text-decoration: none;
        font-size: 13px; font-weight: 700;
    }}
    .pill-btn.secondary {{ background-color: #2a2a2a; }}
    .hero-card {{
        display: flex; gap: 26px; align-items: flex-start;
        background: linear-gradient(120deg, #1a1a1a, #0a0a0a);
        color: #eaeaea; padding: 24px; border-radius: 16px; margin-bottom: 34px;
        border: 1px solid #232323;
    }}
    .hero-poster {{ width: 230px; border-radius: 12px; flex-shrink: 0; }}
    .hero-title {{ font-size: 32px; font-weight: 800; margin-bottom: 8px; }}
    .hero-subtext {{ font-size: 16px; margin-top: 6px; color: #cfcfcf; }}
    .section-title {{
        font-size: 22px; font-weight: 800; margin: 10px 0 16px 0; color: #fff;
        border-left: 4px solid #e50914; padding-left: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# ==== Sidebar ====
with st.sidebar:
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:20px;">
            <img src="data:image/png;base64,{logo_base64}" style="height:32px;"/>
            <span style="color:#e50914;font-weight:800;font-size:18px;">PopFlix</span>
        </div>
    """, unsafe_allow_html=True)

    search_q = st.text_input("🔍 Search", placeholder="Search movies or TV...", key="sidebar_search")

    st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    nav_items = ["Home", "TV Shows", "Movies", "Latest", "My List"]
    for item in nav_items:
        active = st.session_state.page == item
        wrapper_class = "nav-active" if active else ""
        st.markdown(f"<div class='{wrapper_class}'>", unsafe_allow_html=True)
        if st.button(item.upper(), key=f"nav_{item}", use_container_width=True):
            st.session_state.page = item
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# If the sidebar search box has text, treat it as an implicit Movies-page search
if search_q:
    st.session_state.page = "Movies"
    st.session_state.presearch = search_q

# ==== Top bar ====
st.markdown(f"""
    <div class="topbar">
        <div style="width:120px;"></div>
        <div class="brand">
            <img src="data:image/png;base64,{logo_base64}" style="height:44px;"/>
            <h1>PopFlix</h1>
        </div>
        <div class="profile">
            <div class="profile-avatar">🙂</div>
            <span>Guest</span>
        </div>
    </div>
    <p class="tagline">Because scrolling for 45 minutes is a real horror movie.</p>
""", unsafe_allow_html=True)


# ==== Reusable render for a search+recommend flow ====
def render_recommender(media_type, prefill=None):
    label = "movie" if media_type == "movie" else "TV show"
    st.markdown(f"<div class='section-title'>Find your next {label}</div>", unsafe_allow_html=True)
    default_val = prefill or ""
    query = st.text_input("", value=default_val, placeholder=f"e.g. Inception, The Dark Knight, Titanic..."
                           if media_type == "movie" else "e.g. Breaking Bad, Peaky Blinders, Stranger Things...",
                           key=f"query_{media_type}")

    selected_id, selected_label = None, None
    if query:
        with st.spinner("Searching..."):
            matches = search_titles(query, media_type)
        if not matches:
            st.warning(f"No {label} found matching \"{query}\".")
        elif len(matches) == 1:
            selected_id, selected_label = matches[0]["id"], matches[0]["label"]
        else:
            options = {m["label"]: m["id"] for m in matches}
            chosen = st.selectbox("Did you mean:", list(options.keys()), key=f"select_{media_type}")
            selected_id, selected_label = options[chosen], chosen

    # Jump-to from a hero/card click
    if not selected_id and st.session_state.get("jump_id"):
        selected_id = st.session_state.pop("jump_id")
        selected_label = st.session_state.pop("jump_label", "")

    if selected_id:
        title, poster, rating, genres, trailer, overview = fetch_metadata(selected_id, media_type)
        display_title = selected_label or title
        in_list = (str(selected_id), media_type) in st.session_state.watchlist
        list_link = f"?action=remove&id={selected_id}&type={media_type}" if in_list else f"?action=add&id={selected_id}&type={media_type}"
        list_text = "✓ In My List" if in_list else "+ My List"

        st.markdown(f"""
            <div class="hero-card">
                <img src="{poster}" class="hero-poster" />
                <div>
                    <div class="hero-title">{display_title}</div>
                    <div class="hero-subtext">⭐ {rating}</div>
                    <div class="hero-subtext">🎭 {genres}</div>
                    <div class="hero-subtext">{overview}</div>
                    <div class="btn-row" style="justify-content:flex-start;margin-top:16px;">
                        <a class="pill-btn" href="{trailer}" target="_blank">▶ Watch Trailer</a>
                        <a class="pill-btn secondary" href="{list_link}">{list_text}</a>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.spinner("Finding similar titles..."):
            results = recommend(selected_id, media_type)

        st.markdown("<div class='section-title'>You may also like</div>", unsafe_allow_html=True)
        if not results:
            st.info("No recommendations available yet.")
        else:
            cols = st.columns(len(results))
            for i, r in enumerate(results):
                with cols[i]:
                    in_r_list = (str(r["id"]), media_type) in st.session_state.watchlist
                    r_link = f"?action=remove&id={r['id']}&type={media_type}" if in_r_list else f"?action=add&id={r['id']}&type={media_type}"
                    r_text = "✓ Added" if in_r_list else "+ List"
                    view_link = f"?action=view&id={r['id']}&type={media_type}&label={requests.utils.quote(r['title'])}"
                    st.markdown(f"""
                        <div class="movie-card">
                            <a href="{view_link}" style="text-decoration:none;color:inherit;">
                                <img src="{r['poster']}" class="movie-poster" />
                                <div class="movie-title">{r['title']}</div>
                            </a>
                            <div class="movie-subtext">⭐ {r['rating']}</div>
                            <div class="movie-subtext">🎭 {r['genres']}</div>
                            <div class="btn-row">
                                <a class="pill-btn" href="{r['trailer']}" target="_blank">▶ Trailer</a>
                                <a class="pill-btn secondary" href="{r_link}">{r_text}</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)


def render_grid(items, media_type):
    genre_map = fetch_genre_map(media_type)
    cols = st.columns(4)
    for i, item in enumerate(items):
        title = item.get("title") or item.get("name", "")
        poster_path = item.get("poster_path")
        poster = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else PLACEHOLDER
        rating = item.get("vote_average", "N/A")
        genres = ", ".join(genre_map.get(g, "") for g in item.get("genre_ids", [])[:2] if g in genre_map)
        item_id = item["id"]
        in_list = (str(item_id), media_type) in st.session_state.watchlist
        r_link = f"?action=remove&id={item_id}&type={media_type}" if in_list else f"?action=add&id={item_id}&type={media_type}"
        r_text = "✓ Added" if in_list else "+ List"
        view_link = f"?action=view&id={item_id}&type={media_type}&label={requests.utils.quote(title)}"
        with cols[i % 4]:
            st.markdown(f"""
                <div class="movie-card">
                    <a href="{view_link}" style="text-decoration:none;color:inherit;">
                        <img src="{poster}" class="movie-poster" />
                        <div class="movie-title">{title}</div>
                    </a>
                    <div class="movie-subtext">⭐ {rating}</div>
                    <div class="movie-subtext">🎭 {genres}</div>
                    <div class="btn-row">
                        <a class="pill-btn secondary" href="{r_link}">{r_text}</a>
                    </div>
                </div>
            """, unsafe_allow_html=True)


# ==== Pages ====
page = st.session_state.page

if page == "Home":
    st.markdown("<div class='section-title'>Trending now</div>", unsafe_allow_html=True)
    genre_map = fetch_genre_map("movie")
    trending = fetch_trending("movie", 8)
    fan_html = "<div class='fan'>"
    for m in trending:
        poster_path = m.get("poster_path")
        bg = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else PLACEHOLDER
        genre_names = [genre_map.get(g) for g in m.get("genre_ids", []) if genre_map.get(g)]
        label = genre_names[0] if genre_names else (m.get("title") or m.get("name", ""))
        link = f"?action=view&id={m['id']}&type=movie&label={requests.utils.quote(m.get('title', ''))}"
        fan_html += f"""
            <div class="fan-item" style="background-image:url('{bg}');">
                <a href="{link}">
                    <div class="fan-overlay">{label}</div>
                </a>
            </div>
        """
    fan_html += "</div>"
    st.markdown(fan_html, unsafe_allow_html=True)
    render_recommender("movie", prefill=st.session_state.pop("presearch", None))

elif page == "Movies":
    render_recommender("movie", prefill=st.session_state.pop("presearch", None))

elif page == "TV Shows":
    render_recommender("tv")

elif page == "Latest":
    st.markdown("<div class='section-title'>Now playing in theaters</div>", unsafe_allow_html=True)
    now_playing = fetch_now_playing(12)
    if not now_playing:
        st.info("Couldn't load latest releases right now.")
    else:
        render_grid(now_playing, "movie")

elif page == "My List":
    st.markdown("<div class='section-title'>My List</div>", unsafe_allow_html=True)
    if not st.session_state.watchlist:
        st.info("Your list is empty. Add movies or shows from any page with the '+ List' button.")
    else:
        cols = st.columns(4)
        for i, (mid, mtype) in enumerate(st.session_state.watchlist):
            title, poster, rating, genres, trailer, _ = fetch_metadata(mid, mtype)
            r_link = f"?action=remove&id={mid}&type={mtype}"
            view_link = f"?action=view&id={mid}&type={mtype}&label={requests.utils.quote(title)}"
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="movie-card">
                        <a href="{view_link}" style="text-decoration:none;color:inherit;">
                            <img src="{poster}" class="movie-poster" />
                            <div class="movie-title">{title}</div>
                        </a>
                        <div class="movie-subtext">⭐ {rating}</div>
                        <div class="movie-subtext">🎭 {genres}</div>
                        <div class="btn-row">
                            <a class="pill-btn" href="{trailer}" target="_blank">▶ Trailer</a>
                            <a class="pill-btn secondary" href="{r_link}">Remove</a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
