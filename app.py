import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import asyncio
import time

# Import our database mediation layer
#from database_wrapper import db_mediator, initialize_remote_databases, cached_search, cached_stats, get_health_status

# Set page config
st.set_page_config(
    page_title="BingeBox - Database Mediation",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark theme with proper text containment
st.markdown("""
<style>
    /* Dark theme for main app */
    .stApp {
        background: #0e1117;
        color: #ffffff;
    }
    
    .main-header {
        font-size: 3rem;
        color: #e50914;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Container styling to contain all content */
    .filter-container, .mediation-container, .chatbot-container, .schema-container {
        padding: 0;
        margin: 0;
    }
    
    .filter-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        height: 600px;
        overflow-y: auto;
    }
    
    .llm-chatbot {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        height: 600px;
        overflow-y: auto;
    }
    
    .mediation-query {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        height: 280px;
        overflow-y: auto;
    }
    
    .global-schema {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        margin: 0.5rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        height: 500px;
        overflow-y: auto;
    }
    
    .movie-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white !important;
    }
    
    .series-card {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white !important;
    }
    
    .chat-message {
        background: rgba(255,255,255,0.1);
        padding: 0.8rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid rgba(255,255,255,0.3);
        color: white !important;
    }
    
    .user-message {
        background: rgba(255,255,255,0.2);
        text-align: right;
        border-left: none;
        border-right: 4px solid rgba(255,255,255,0.3);
        color: white !important;
    }
    
    /* Input styling for dark theme */
    .stSelectbox > div > div > div {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    .stMultiSelect > div > div > div {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    .stNumberInput > div > div > input {
        background-color: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    .stCheckbox > label {
        color: white !important;
    }
    
    .stButton > button {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }
    
    .stButton > button:hover {
        background: rgba(255,255,255,0.2) !important;
        color: white !important;
    }
    
    /* Hide Streamlit default styling that conflicts */
    .stSelectbox label, .stTextInput label, .stMultiSelect label, .stNumberInput label {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Metric styling */
    .stMetric {
        background: rgba(255,255,255,0.1);
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.2rem 0;
    }
    
    .stMetric label {
        color: white !important;
        font-size: 0.8rem !important;
    }
    
    .stMetric div[data-testid="metric-value"] {
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database connections
@st.cache_resource
def init_databases():
    """Initialize database mediator"""
    try:
        mediator = initialize_remote_databases()
        # Run async initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        connected_count = loop.run_until_complete(mediator.initialize_connections())
        loop.close()
        return mediator, connected_count
    except Exception as e:
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

# Main layout following your sketch
# Top row: Filter Box, Mediation Query, LLM Chatbot
top_col1, top_col2, top_col3 = st.columns([1, 2, 1])

# FILTER BOX (Left top)
with top_col1:
    with st.container():
        st.markdown('<div class="filter-box">', unsafe_allow_html=True)
        st.markdown("### 🔍 Filter Box")
    
    # Basic search filters
    search_term = st.text_input(
        "Search Term",
        placeholder="Enter movie or series name...",
        key="filter_search"
    )
    
    search_field = st.selectbox(
        "Search Field",
        ["title", "genre", "director", "cast", "network", "year", "rating"],
        key="filter_field"
    )
    
    # Database selection
    st.markdown("**Database Sources:**")
    include_movies = st.checkbox("🎬 Include Movies", value=True, key="filter_movies")
    include_series = st.checkbox("📺 Include Series", value=True, key="filter_series")
    
    # Genre filters
    genre_options = st.multiselect(
        "Genres",
        ["Action", "Comedy", "Drama", "Horror", "Sci-Fi", "Romance", "Thriller", "Crime", "Fantasy", "Documentary"],
        key="filter_genres"
    )
    
    # Year range
    col_year1, col_year2 = st.columns(2)
    with col_year1:
        year_from = st.number_input("Year From", min_value=1900, max_value=2024, value=2000, key="filter_year_from")
    with col_year2:
        year_to = st.number_input("Year To", min_value=1900, max_value=2024, value=2024, key="filter_year_to")
    
    # Rating filter
    min_rating = st.number_input("Minimum Rating", min_value=0.0, max_value=10.0, value=0.0, step=0.1, key="filter_rating")
    
    # Results limit
    results_limit = st.number_input("Results Limit", min_value=5, max_value=100, value=25, key="filter_limit")
    
    # Network filter for series
    network_options = st.multiselect(
        "Networks",
        ["Netflix", "HBO", "Amazon Prime", "Disney+", "Hulu", "NBC", "CBS", "Fox", "AMC", "BBC"],
        key="filter_networks"
    )
        
    st.markdown('</div>', unsafe_allow_html=True)

# MEDIATION QUERY (Center top)
with top_col2:
    with st.container():
        st.markdown('<div class="mediation-query">', unsafe_allow_html=True)
        st.markdown("### 🔄 Mediation Query")
    
    # Query tabs
    query_tab = st.selectbox(
        "Query Type",
        ["Search", "Statistics", "Health Check"],
        key="query_tab"
    )
    
    # Query input
    query_input = st.text_input(
        "Enter Query",
        placeholder="Search across distributed databases...",
        key="mediation_query"
    )
    
    # Execute button
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        execute_search = st.button("🚀 Execute Search", type="primary")
    with col_btn2:
        get_stats = st.button("📊 Get Stats")
    with col_btn3:
        health_check = st.button("🏥 Health Check")
    
    # Quick stats display
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
        
        st.markdown('</div>', unsafe_allow_html=True)

# LLM CHATBOT (Right top)
with top_col3:
    with st.container():
        st.markdown('<div class="llm-chatbot">', unsafe_allow_html=True)
        st.markdown("### 🤖 LLM Chatbot")
    
    # Chat messages display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages[-10:]:  # Show last 10 messages
            if msg["role"] == "bot":
                st.markdown(f'<div class="chat-message">🤖 <strong>BingeBot:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message user-message">👤 <strong>You:</strong> {msg["message"]}</div>', unsafe_allow_html=True)
    
    # Chat input
    chat_input = st.text_input(
        "Ask BingeBot",
        placeholder="Ask about movies, series, or database...",
        key="chat_input"
    )
    
    if st.button("💬 Send", key="send_chat") and chat_input:
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "message": chat_input})
        
        # Generate bot response
        if "movie" in chat_input.lower():
            bot_response = f"I can help you find movies! Try searching for specific titles, genres, or directors using the search functionality."
        elif "series" in chat_input.lower() or "show" in chat_input.lower():
            bot_response = f"Looking for TV series? Use the filters to narrow down by network, genre, or rating."
        elif "database" in chat_input.lower():
            bot_response = f"Our system connects to {connected_dbs} databases via Tailscale. Movies are stored in PostgreSQL, Series in MySQL."
        elif "search" in chat_input.lower():
            bot_response = "You can search by title, genre, director, cast, network, year, or rating. Use the filters on the left!"
        else:
            bot_response = "I can help with movie/series searches, database info, or recommendations. What would you like to know?"
        
        st.session_state.chat_messages.append({"role": "bot", "message": bot_response})
        st.rerun()
    
        st.markdown('</div>', unsafe_allow_html=True)

# GLOBAL SCHEMA VIEW RESULT (Bottom full width)
with st.container():
    st.markdown('<div class="global-schema">', unsafe_allow_html=True)
    st.markdown("### 🌐 Global Schema View Result")

# Execute search logic
if execute_search or query_input:
    search_query = query_input or search_term
    
    if search_query:
        with st.spinner(f"Searching for '{search_query}' across distributed databases..."):
            try:
                # Execute search across databases
                results = cached_search(search_query, search_field) if mediator else {}
                st.session_state.search_results = results
                
                if results:
                    # Display results summary
                    total_results = sum(len(result_list) for result_list in results.values() if result_list)
                    st.info(f"🎯 Found {total_results} results across {len(results)} databases")
                    
                    # Create columns for results
                    result_col1, result_col2 = st.columns(2)
                    
                    # Movies results
                    if "movies" in results and include_movies and results["movies"]:
                        with result_col1:
                            st.markdown("#### 🎬 Movies Database Results")
                            movies_data = results["movies"]
                            
                            for movie in movies_data[:int(results_limit)]:
                                if (not genre_options or any(g.lower() in movie.get('genre', '').lower() for g in genre_options)) and \
                                   (movie.get('rating', 0) >= min_rating) and \
                                   (year_from <= movie.get('year', 0) <= year_to):
                                    st.markdown(f"""
                                    <div class="movie-card">
                                        <h4>🎬 {movie.get('title', 'Unknown')}</h4>
                                        <p><strong>Year:</strong> {movie.get('year', 'N/A')}</p>
                                        <p><strong>Genre:</strong> {movie.get('genre', 'N/A')}</p>
                                        <p><strong>Rating:</strong> ⭐ {movie.get('rating', 'N/A')}/10</p>
                                        <p><strong>Director:</strong> {movie.get('director', 'N/A')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    # Series results  
                    if "series" in results and include_series and results["series"]:
                        with result_col2:
                            st.markdown("#### 📺 Series Database Results")
                            series_data = results["series"]
                            
                            for series in series_data[:int(results_limit)]:
                                if (not genre_options or any(g.lower() in series.get('genre', '').lower() for g in genre_options)) and \
                                   (not network_options or series.get('network', '') in network_options) and \
                                   (series.get('rating', 0) >= min_rating):
                                    st.markdown(f"""
                                    <div class="series-card">
                                        <h4>📺 {series.get('title', 'Unknown')}</h4>
                                        <p><strong>Seasons:</strong> {series.get('seasons', 'N/A')}</p>
                                        <p><strong>Genre:</strong> {series.get('genre', 'N/A')}</p>
                                        <p><strong>Rating:</strong> ⭐ {series.get('rating', 'N/A')}/10</p>
                                        <p><strong>Network:</strong> {series.get('network', 'N/A')}</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                else:
                    st.warning("No results found. Check database connections.")
                    
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")
    else:
        st.info("👆 Enter a search term in the Mediation Query or Filter Box to search both databases")

# Show statistics
elif get_stats:
    try:
        with st.spinner("Fetching database statistics..."):
            stats = cached_stats() if mediator else {}
            
            if stats:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🎬 Movies Database Stats")
                    movies_stats = stats.get("movies", [{}])[0] if stats.get("movies") else {}
                    if movies_stats:
                        for key, value in movies_stats.items():
                            st.metric(key.replace('_', ' ').title(), value)
                
                with col2:
                    st.markdown("#### 📺 Series Database Stats")
                    series_stats = stats.get("series", [{}])[0] if stats.get("series") else {}
                    if series_stats:
                        for key, value in series_stats.items():
                            st.metric(key.replace('_', ' ').title(), value)
            else:
                st.warning("Unable to fetch database statistics")
    except Exception as e:
        st.error(f"❌ Failed to load statistics: {str(e)}")

# Health check
elif health_check:
    try:
        with st.spinner("Performing health check..."):
            health_status = get_health_status() if mediator else {}
            
            if health_status:
                for db_name, status in health_status.items():
                    status_color = "🟢" if status.get('status') == 'connected' else "🔴"
                    st.markdown(f"""
                    **{status_color} {db_name.title()} Database**
                    - Status: {status.get('status', 'Unknown').upper()}
                    - Host: {status.get('host', 'N/A')}
                    - Response Time: {status.get('response_time', 'N/A')}
                    - Version: {status.get('version', 'N/A')}
                    """)
            else:
                st.warning("Health check unavailable")
    except Exception as e:
        st.error(f"❌ Health check failed: {str(e)}")

else:
    st.info("🔍 Use the Mediation Query section above to search, get statistics, or perform health checks")

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🌐 BingeBox - Distributed Database Mediation System | Connected via Tailscale | 
        <a href="https://github.com/deepankar-MT24031/iia_test" target="_blank">GitHub Repository</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
