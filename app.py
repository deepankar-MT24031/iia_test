import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import asyncio

# Import database mediation layer
#from database_wrapper import db_mediator, initialize_remote_databases, cached_search, cached_stats, get_health_status

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="BingeBox - Database Mediation",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
/* Dark theme */
.stApp { background: #0e1117; color: #ffffff; }

.main-header { font-size: 3rem; color: #e50914; text-align: center; margin-bottom: 1rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }

.filter-box, .mediation-query, .llm-chatbot, .global-schema { 
    padding: 1rem; border-radius: 15px; color: white !important; margin: 0.5rem 0; box-shadow: 0 8px 32px rgba(0,0,0,0.3); overflow-y: auto; 
}
.filter-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 600px; }
.llm-chatbot { background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); height: 600px; }
.mediation-query { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); height: 280px; }
.global-schema { background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%); height: 500px; }

/* Cards */
.movie-card { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; color: white !important; }
.series-card { background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%); padding: 1rem; border-radius: 10px; margin: 0.5rem 0; color: white !important; }

/* Chat messages */
.chat-message { background: rgba(255,255,255,0.1); padding: 0.8rem; border-radius: 10px; margin: 0.5rem 0; border-left: 4px solid rgba(255,255,255,0.3); color: white !important; }
.user-message { background: rgba(255,255,255,0.2); text-align: right; border-left: none; border-right: 4px solid rgba(255,255,255,0.3); color: white !important; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox div, .stMultiSelect div { background-color: rgba(255,255,255,0.1) !important; color: white !important; border: 1px solid rgba(255,255,255,0.3) !important; }

/* Buttons */
.stButton>button { background: rgba(255,255,255,0.1) !important; color: white !important; border: 1px solid rgba(255,255,255,0.3) !important; }
.stButton>button:hover { background: rgba(255,255,255,0.2) !important; color: white !important; }

/* Metrics */
.stMetric { background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 8px; margin: 0.2rem 0; }
.stMetric label { color: white !important; font-size: 0.8rem !important; }
.stMetric div[data-testid="metric-value"] { color: white !important; font-size: 1.5rem !important; font-weight: bold !important; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE INITIALIZATION ---
@st.cache_resource
def init_databases():
    try:
        mediator = initialize_remote_databases()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        connected_count = loop.run_until_complete(mediator.initialize_connections())
        loop.close()
        return mediator, connected_count
    except Exception:
        return None, 0

mediator, connected_dbs = init_databases()

# --- SESSION STATE ---
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [{"role": "bot", "message": "Hi! I'm BingeBot. Ask me about movies, series, or database operations!"}]
if "search_results" not in st.session_state:
    st.session_state.search_results = None

# --- HEADER ---
st.markdown('<h1 class="main-header">🎬 BingeBox</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">C (Mediation) - Intelligent Database Mediation System</p>', unsafe_allow_html=True)

# --- TOP ROW: FILTER, MEDIATION, CHATBOT ---
top_col1, top_col2, top_col3 = st.columns([1,2,1])

# --- FILTER BOX ---
with top_col1:
    st.markdown('<div class="filter-box">', unsafe_allow_html=True)
    st.markdown("### 🔍 Filter Box")
    search_term = st.text_input("Search Term", placeholder="Enter movie or series name...", key="filter_search")
    search_field = st.selectbox("Search Field", ["title", "genre", "director", "cast", "network", "year", "rating"], key="filter_field")
    st.markdown("**Database Sources:**")
    include_movies = st.checkbox("🎬 Include Movies", value=True)
    include_series = st.checkbox("📺 Include Series", value=True)
    genre_options = st.multiselect("Genres", ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Crime", "Fantasy", "Documentary"])
    col_year1, col_year2 = st.columns(2)
    with col_year1: year_from = st.number_input("Year From", 1900, 2024, 2000)
    with col_year2: year_to = st.number_input("Year To", 1900, 2024, 2024)
    min_rating = st.number_input("Minimum Rating", 0.0, 10.0, 0.0, 0.1)
    results_limit = st.number_input("Results Limit", 5, 100, 25)
    network_options = st.multiselect("Networks", ["Netflix", "HBO", "Amazon Prime", "Disney+", "Hulu", "NBC", "CBS", "Fox", "AMC", "BBC"])
    st.markdown('</div>', unsafe_allow_html=True)

# --- MEDIATION QUERY ---
with top_col2:
    st.markdown('<div class="mediation-query">', unsafe_allow_html=True)
    st.markdown("### 🔄 Mediation Query")
    query_tab = st.selectbox("Query Type", ["Search", "Statistics", "Health Check"])
    query_input = st.text_input("Enter Query", placeholder="Search across distributed databases...")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1: execute_search = st.button("🚀 Execute Search")
    with col_btn2: get_stats = st.button("📊 Get Stats")
    with col_btn3: health_check = st.button("🏥 Health Check")

    # Quick stats
    try:
        stats = cached_stats() if mediator else {}
        movies_stats = stats.get("movies", [{}])[0] if stats.get("movies") else {}
        series_stats = stats.get("series", [{}])[0] if stats.get("series") else {}
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1: st.metric("🎬 Movies", f"{movies_stats.get('total_movies',0):,}")
        with stat_col2: st.metric("📺 Series", f"{series_stats.get('total_series',0):,}")
        with stat_col3: st.metric("🔗 Connected", f"{connected_dbs}/2")
    except Exception: st.info("Stats unavailable")
    st.markdown('</div>', unsafe_allow_html=True)

# --- LLM CHATBOT ---
with top_col3:
    st.markdown('<div class="llm-chatbot">', unsafe_allow_html=True)
    st.markdown("### 🤖 LLM Chatbot")
    chat_container = st.container()
    for msg in st.session_state.chat_messages[-10:]:
        if msg["role"] == "bot":
            st.markdown(f'<div class="chat-message">🤖 <strong>BingeBot:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-message user-message">👤 <strong>You:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
    chat_input = st.text_input("Ask BingeBot", placeholder="Ask about movies, series, or database...", key="chat_input")
    if st.button("💬 Send") and chat_input:
        st.session_state.chat_messages.append({"role":"user","message":chat_input})
        # Bot logic
        if "movie" in chat_input.lower(): bot_response = "I can help you find movies! Use the filters on the left."
        elif "series" in chat_input.lower() or "show" in chat_input.lower(): bot_response = "Looking for TV series? Use filters by network/genre."
        elif "database" in chat_input.lower(): bot_response = f"Our system connects to {connected_dbs} databases."
        else: bot_response = "I can help with movie/series searches or database info."
        st.session_state.chat_messages.append({"role":"bot","message":bot_response})
        st.experimental_rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- GLOBAL SCHEMA VIEW ---
st.markdown('<div class="global-schema">', unsafe_allow_html=True)
st.markdown("### 🌐 Global Schema View Result")
st.markdown('</div>', unsafe_allow_html=True)

# --- ACTION LOGIC ---
if execute_search or query_input:
    search_query = query_input or search_term
    if search_query:
        with st.spinner(f"Searching '{search_query}'..."):
            try:
                results = cached_search(search_query, search_field) if mediator else {}
                st.session_state.search_results = results
                if results:
                    total_results = sum(len(v) for v in results.values() if v)
                    st.info(f"🎯 Found {total_results} results across {len(results)} databases")
                    result_col1, result_col2 = st.columns(2)
                    # Movies
                    if "movies" in results and include_movies:
                        with result_col1: st.markdown("#### 🎬 Movies Database Results")
                        for movie in results["movies"][:int(results_limit)]:
                            if (not genre_options or any(g.lower() in movie.get('genre','').lower() for g in genre_options)) and (movie.get('rating',0)>=min_rating) and (year_from <= movie.get('year',0) <= year_to):
                                st.markdown(f"""
                                    <div class="movie-card">
                                    <h4>🎬 {movie.get('title','Unknown')}</h4>
                                    <p><strong>Year:</strong> {movie.get('year','N/A')}</p>
                                    <p><strong>Genre:</strong> {movie.get('genre','N/A')}</p>
                                    <p><strong>Rating:</strong> ⭐ {movie.get('rating','N/A')}/10</p>
                                    <p><strong>Director:</strong> {movie.get('director','N/A')}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                    # Series
                    if "series" in results and include_series:
                        with result_col2: st.markdown("#### 📺 Series Database Results")
                        for series in results["series"][:int(results_limit)]:
                            if (not genre_options or any(g.lower() in series.get('genre','').lower() for g in genre_options)) and (not network_options or series.get('network','') in network_options) and (series.get('rating',0)>=min_rating):
                                st.markdown(f"""
                                    <div class="series-card">
                                    <h4>📺 {series.get('title','Unknown')}</h4>
                                    <p><strong>Seasons:</strong> {series.get('seasons','N/A')}</p>
                                    <p><strong>Genre:</strong> {series.get('genre','N/A')}</p>
                                    <p><strong>Rating:</strong> ⭐ {series.get('rating','N/A')}/10</p>
                                    <p><strong>Network:</strong> {series.get('network','N/A')}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                else: st.warning("No results found.")
            except Exception as e: st.error(f"❌ Search failed: {e}")
    else: st.info("👆 Enter a search term in the Mediation Query or Filter Box.")

elif get_stats:
    try:
        with st.spinner("Fetching database statistics..."):
            stats = cached_stats() if mediator else {}
            if stats:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### 🎬 Movies Database Stats")
                    movies_stats = stats.get("movies",[{}])[0]
                    for k,v in movies_stats.items(): st.metric(k.replace('_',' ').title(), v)
                with col2:
                    st.markdown("#### 📺 Series Database Stats")
                    series_stats = stats.get("series",[{}])[0]
                    for k,v in series_stats.items(): st.metric(k.replace('_',' ').title(), v)
            else: st.warning("Unable to fetch database statistics")
    except Exception as e: st.error(f"❌ Failed to load statistics: {e}")

elif health_check:
    try:
        with st.spinner("Performing health check..."):
            health_status = get_health_status() if mediator else {}
            if health_status:
                for db_name, status in health_status.items():
                    status_color = "🟢" if status.get('status')=='connected' else "🔴"
                    st.markdown(f"**{status_color} {db_name.title()} Database** - Status: {status.get('status','Unknown').upper()} - Host: {status.get('host','N/A')} - Response Time: {status.get('response_time','N/A')} - Version: {status.get('version','N/A')}")
            else: st.warning("Health check unavailable")
    except Exception as e: st.error(f"❌ Health check failed: {e}")

else:
    st.info("🔍 Use the Mediation Query section above to search, get statistics, or perform health checks")

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; padding:1rem;">
<p>🌐 BingeBox - Distributed Database Mediation System | Connected via Tailscale | 
<a href="https://github.com/deepankar-MT24031/iia_test" target="_blank">GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)
