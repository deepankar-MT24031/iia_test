import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import asyncio
import time

# Import our database mediation layer
# from database_wrapper import db_mediator, initialize_remote_databases, cached_search, cached_stats, get_health_status

# Set page config
st.set_page_config(
    page_title="BingeBox - Database Mediation",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme
st.markdown("""
<style>
/* ... your existing CSS ... */
</style>
""", unsafe_allow_html=True)

# Initialize database connections
@st.cache_resource
def init_databases():
    """Initialize database mediator"""
    try:
        mediator = initialize_remote_databases()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        connected_count = loop.run_until_complete(mediator.initialize_connections())
        loop.close()
        return mediator, connected_count
    except Exception:
        return None, 0

# Initialize session state for chat
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "bot", "message": "Hi! I'm BingeBot. Ask me about movies, series, or database operations!"}
    ]

if "search_results" not in st.session_state:
    st.session_state.search_results = None

# Title and Header
st.markdown('<h1 class="main-header">🎬 BingeBox</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">C (Mediation) - Intelligent Database Mediation System</p>', unsafe_allow_html=True)

# Initialize databases
try:
    mediator, connected_dbs = init_databases()
    if connected_dbs > 0:
        st.success(f"✅ Connected to {connected_dbs} remote databases via Tailscale")
    else:
        st.error("❌ Failed to connect to remote databases")
except Exception as e:
    st.error(f"❌ Database initialization failed: {str(e)}")
    mediator, connected_dbs = None, 0

# Main layout: Top row
top_col1, top_col2, top_col3 = st.columns([1, 2, 1])

# FILTER BOX
with top_col1:
    st.markdown('<div class="filter-box"><div class="box-content">', unsafe_allow_html=True)
    st.markdown("### 🔍 Filter Box")

    search_term = st.text_input("Search Term", placeholder="Enter movie or series name...", key="filter_search")
    search_field = st.selectbox("Search Field", ["title", "genre", "director", "cast", "network", "year", "rating"], key="filter_field")
    st.markdown("**Database Sources:**")
    include_movies = st.checkbox("🎬 Include Movies", value=True, key="filter_movies")
    include_series = st.checkbox("📺 Include Series", value=True, key="filter_series")

    genre_options = st.multiselect(
        "Genres",
        ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Crime", "Fantasy", "Documentary"],
        key="filter_genres"
    )

    col_year1, col_year2 = st.columns(2)
    with col_year1:
        year_from = st.number_input("Year From", min_value=1900, max_value=2024, value=2000, key="filter_year_from")
    with col_year2:
        year_to = st.number_input("Year To", min_value=1900, max_value=2024, value=2024, key="filter_year_to")

    min_rating = st.number_input("Minimum Rating", min_value=0.0, max_value=10.0, value=0.0, step=0.1, key="filter_rating")
    results_limit = st.number_input("Results Limit", min_value=5, max_value=100, value=25, key="filter_limit")
    network_options = st.multiselect(
        "Networks",
        ["Netflix", "HBO", "Amazon Prime", "Disney+", "Hulu", "NBC", "CBS", "Fox", "AMC", "BBC"],
        key="filter_networks"
    )
    st.markdown('</div></div>', unsafe_allow_html=True)

# MEDIATION QUERY
with top_col2:
    st.markdown('<div class="mediation-query"><div class="box-content">', unsafe_allow_html=True)
    st.markdown("### 🔄 Mediation Query")

    query_tab = st.selectbox("Query Type", ["Search", "Statistics", "Health Check"], key="query_tab")
    query_input = st.text_input("Enter Query", placeholder="Search across distributed databases...", key="mediation_query")

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        execute_search = st.button("🚀 Execute Search", type="primary")
    with col_btn2:
        get_stats = st.button("📊 Get Stats")
    with col_btn3:
        health_check = st.button("🏥 Health Check")

    try:
        stats = cached_stats() if mediator else {}
        movies_stats = stats.get("movies", [{}])[0] if stats.get("movies") else {}
        series_stats = stats.get("series", [{}])[0] if stats.get("series") else {}
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        with stat_col1:
            st.metric("🎬 Movies", f"{movies_stats.get('total_movies', 0):,}")
        with stat_col2:
            st.metric("📺 Series", f"{series_stats.get('total_series', 0):,}")
        with stat_col3:
            st.metric("🔗 Connected", f"{connected_dbs}/2")
    except:
        st.info("Stats unavailable")

    st.markdown('</div></div>', unsafe_allow_html=True)

# LLM CHATBOT
with top_col3:
    st.markdown('<div class="llm-chatbot"><div class="box-content">', unsafe_allow_html=True)
    st.markdown("### 🤖 LLM Chatbot")

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages[-10:]:
            if msg["role"] == "bot":
                st.markdown(f'<div class="chat-message">🤖 <strong>BingeBot:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message user-message">👤 <strong>You:</strong> {msg["message"]}</div>', unsafe_allow_html=True)

    chat_input = st.text_input("Ask BingeBot", placeholder="Ask about movies, series, or database...", key="chat_input")
    if st.button("💬 Send", key="send_chat") and chat_input:
        st.session_state.chat_messages.append({"role": "user", "message": chat_input})
        bot_response = "I can help with movie/series searches, database info, or recommendations."
        st.session_state.chat_messages.append({"role": "bot", "message": bot_response})
        st.rerun()

    st.markdown('</div></div>', unsafe_allow_html=True)

# GLOBAL SCHEMA VIEW RESULT
st.markdown('<div class="global-schema"><div class="box-content">', unsafe_allow_html=True)
st.markdown("### 🌐 Global Schema View Result")

# Correct indentation: top-level, no extra spaces
if execute_search or query_input:
    search_query = query_input or search_term
    if search_query:
        st.info(f"Searching for '{search_query}' across databases...")  # Placeholder
elif get_stats:
    st.info("Fetching database statistics...")  # Placeholder
elif health_check:
    st.info("Performing health check...")  # Placeholder
else:
    st.info("🔍 Use the Mediation Query section above to search, get statistics, or perform health checks")

st.markdown('</div></div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>🌐 BingeBox - Distributed Database Mediation System | Connected via Tailscale | 
    <a href="https://github.com/deepankar-MT24031/iia_test" target="_blank">GitHub Repository</a></p>
</div>
""", unsafe_allow_html=True)
