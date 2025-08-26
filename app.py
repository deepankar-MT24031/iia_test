import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import asyncio
import time

# Import our database mediation layer
from database_wrapper import db_mediator, initialize_remote_databases, cached_search, cached_stats, get_health_status

# Set page config
st.set_page_config(
    page_title="Movies & Series Database",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #e50914;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .database-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .movie-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    .series-card {
        background: linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        color: white;
    }
    .search-box {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
    }
    .status-connected {
        color: #28a745;
        font-weight: bold;
    }
    .status-failed {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database connections
@st.cache_resource
def init_databases():
    """Initialize database mediator"""
    mediator = initialize_remote_databases()
    # Run async initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    connected_count = loop.run_until_complete(mediator.initialize_connections())
    loop.close()
    return mediator, connected_count

# Title and Header
st.markdown('<h1 class="main-header">🎬 Movies & Series Database</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Distributed database search across Tailscale network</p>', unsafe_allow_html=True)

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

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x150/e50914/white?text=🎬+Database", width=300)
    st.markdown("### 🔍 Search Options")
    
    # Search configuration
    search_term = st.text_input(
        "Search Term",
        placeholder="Enter movie or series name...",
        help="Search across both Movies and Series databases"
    )
    
    search_type = st.selectbox(
        "Search Field",
        ["title", "genre", "director", "cast", "network"],
        help="Field to search in"
    )
    
    search_limit = st.slider(
        "Results Limit",
        min_value=10,
        max_value=100,
        value=25,
        help="Maximum results per database"
    )
    
    st.markdown("---")
    
    # Database filters
    st.markdown("### 📊 Database Filters")
    include_movies = st.checkbox("Include Movies", value=True)
    include_series = st.checkbox("Include Series", value=True)
    
    min_rating = st.slider(
        "Minimum Rating",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.1
    )
    
    # Refresh button
    if st.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Search", "📊 Statistics", "🎬 Movies", "📺 Series", "⚙️ System"])

with tab1:
    st.subheader("🔍 Global Search")
    
    # Search interface
    with st.container():
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            quick_search = st.text_input(
                "Quick Search",
                value=search_term,
                placeholder="Search movies and series...",
                label_visibility="collapsed"
            )
        
        with col2:
            search_btn = st.button("🔍 Search", type="primary")
        
        with col3:
            clear_btn = st.button("🗑️ Clear")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Perform search
    if (search_btn and quick_search) or search_term:
        search_query = quick_search or search_term
        
        with st.spinner(f"Searching for '{search_query}' across remote databases..."):
            try:
                # Execute search across databases
                results = cached_search(search_query, search_type)
                
                if results:
                    # Display results summary
                    total_results = sum(len(result_list) for result_list in results.values())
                    st.info(f"🎯 Found {total_results} results across {len(results)} databases")
                    
                    # Create columns for results
                    col1, col2 = st.columns(2)
                    
                    # Movies results
                    if "movies" in results and include_movies:
                        with col1:
                            st.markdown("### 🎬 Movies")
                            movies_data = results["movies"]
                            
                            if movies_data:
                                for movie in movies_data[:search_limit]:
                                    if movie.get('rating', 0) >= min_rating:
                                        st.markdown(f"""
                                        <div class="movie-card">
                                            <h4>🎬 {movie.get('title', 'Unknown')}</h4>
                                            <p><strong>Year:</strong> {movie.get('year', 'N/A')}</p>
                                            <p><strong>Genre:</strong> {movie.get('genre', 'N/A')}</p>
                                            <p><strong>Rating:</strong> ⭐ {movie.get('rating', 'N/A')}/10</p>
                                            <p><strong>Director:</strong> {movie.get('director', 'N/A')}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                            else:
                                st.info("No movies found matching your criteria")
                    
                    # Series results  
                    if "series" in results and include_series:
                        with col2:
                            st.markdown("### 📺 Series")
                            series_data = results["series"]
                            
                            if series_data:
                                for series in series_data[:search_limit]:
                                    if series.get('rating', 0) >= min_rating:
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
                                st.info("No series found matching your criteria")
                else:
                    st.warning("No results found. Check database connections.")
                    
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")
    
    elif clear_btn:
        st.rerun()
        
    else:
        st.info("👆 Enter a search term above to query both databases simultaneously")

with tab2:
    st.subheader("📊 Database Statistics")
    
    try:
        stats = cached_stats()
        
        if stats:
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            
            movies_stats = stats.get("movies", [{}])[0] if stats.get("movies") else {}
            series_stats = stats.get("series", [{}])[0] if stats.get("series") else {}
            
            with col1:
                total_movies = movies_stats.get('total_movies', 0)
                st.metric("🎬 Total Movies", f"{total_movies:,}")
            
            with col2:
                total_series = series_stats.get('total_series', 0)
                st.metric("📺 Total Series", f"{total_series:,}")
            
            with col3:
                avg_movie_rating = movies_stats.get('avg_rating', 0)
                st.metric("⭐ Avg Movie Rating", f"{avg_movie_rating:.1f}/10" if avg_movie_rating else "N/A")
            
            with col4:
                avg_series_rating = series_stats.get('avg_rating', 0)
                st.metric("⭐ Avg Series Rating", f"{avg_series_rating:.1f}/10" if avg_series_rating else "N/A")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Database comparison chart
                if total_movies or total_series:
                    db_comparison = pd.DataFrame({
                        'Database': ['Movies', 'Series'],
                        'Count': [total_movies, total_series],
                        'Type': ['🎬 Movies', '📺 Series']
                    })
                    
                    fig_bar = px.bar(
                        db_comparison,
                        x='Database',
                        y='Count',
                        color='Type',
                        title="Content Distribution",
                        color_discrete_map={'🎬 Movies': '#ff6b6b', '📺 Series': '#4ecdc4'}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Rating comparison
                if avg_movie_rating or avg_series_rating:
                    rating_data = pd.DataFrame({
                        'Category': ['Movies', 'Series'],
                        'Average Rating': [avg_movie_rating or 0, avg_series_rating or 0]
                    })
                    
                    fig_rating = px.bar(
                        rating_data,
                        x='Category',
                        y='Average Rating',
                        title="Average Ratings Comparison",
                        color='Average Rating',
                        color_continuous_scale='viridis'
                    )
                    fig_rating.update_layout(yaxis_range=[0, 10])
                    st.plotly_chart(fig_rating, use_container_width=True)
        
        else:
            st.warning("Unable to fetch database statistics")
            
    except Exception as e:
        st.error(f"❌ Failed to load statistics: {str(e)}")

with tab3:
    st.subheader("🎬 Movies Database")
    
    # Movies-specific search and display
    if st.button("🔍 Browse Latest Movies"):
        with st.spinner("Fetching movies from remote database..."):
            try:
                results = cached_search("", "title")  # Get all movies
                movies_data = results.get("movies", [])
                
                if movies_data:
                    # Create DataFrame for better display
                    movies_df = pd.DataFrame(movies_data)
                    
                    # Display as interactive table
                    st.dataframe(
                        movies_df,
                        use_container_width=True,
                        column_config={
                            "title": st.column_config.TextColumn("Title", width="large"),
                            "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
                            "year": st.column_config.NumberColumn("Year"),
                            "genre": st.column_config.TextColumn("Genre"),
                        }
                    )
                else:
                    st.info("No movies data available")
                    
            except Exception as e:
                st.error(f"❌ Failed to fetch movies: {str(e)}")

with tab4:
    st.subheader("📺 Series Database")
    
    # Series-specific search and display
    if st.button("🔍 Browse Latest Series"):
        with st.spinner("Fetching series from remote database..."):
            try:
                results = cached_search("", "title")  # Get all series
                series_data = results.get("series", [])
                
                if series_data:
                    # Create DataFrame for better display
                    series_df = pd.DataFrame(series_data)
                    
                    # Display as interactive table
                    st.dataframe(
                        series_df,
                        use_container_width=True,
                        column_config={
                            "title": st.column_config.TextColumn("Title", width="large"),
                            "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
                            "seasons": st.column_config.NumberColumn("Seasons"),
                            "genre": st.column_config.TextColumn("Genre"),
                            "network": st.column_config.TextColumn("Network"),
                        }
                    )
                else:
                    st.info("No series data available")
                    
            except Exception as e:
                st.error(f"❌ Failed to fetch series: {str(e)}")

with tab5:
    st.subheader("⚙️ System Status")
    
    # Database health check
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🏥 Database Health Check")
        
        if st.button("🔄 Run Health Check"):
            with st.spinner("Checking database connections..."):
                try:
                    health_status = get_health_status()
                    
                    for db_name, status in health_status.items():
                        status_class = "status-connected" if status.get('status') == 'connected' else "status-failed"
                        
                        st.markdown(f"""
                        <div class="database-card">
                            <h4>{db_name.title()} Database</h4>
                            <p><strong>Status:</strong> <span class="{status_class}">{status.get('status', 'Unknown').upper()}</span></p>
                            <p><strong>Host:</strong> {status.get('host', 'N/A')}</p>
                            <p><strong>Response Time:</strong> {status.get('response_time', 'N/A')}</p>
                            <p><strong>Version:</strong> {status.get('version', 'N/A')}</p>
                            {f"<p><strong>Error:</strong> {status.get('error', 'N/A')}</p>" if status.get('error') else ""}
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"❌ Health check failed: {str(e)}")
    
    with col2:
        st.markdown("### 🔧 System Info")
        st.info(f"**Connected DBs:** {connected_dbs}/2")
        st.info(f"**Cache Status:** {'Active' if st.cache_data else 'Inactive'}")
        st.info(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")
        
        # Clear cache button
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared successfully!")
    
    # Configuration display
    st.markdown("### ⚙️ Database Configuration")
    
    config_info = {
        "Movies DB": {
            "Type": "PostgreSQL",
            "Network": "Tailscale",
            "Status": "Remote"
        },
        "Series DB": {
            "Type": "MySQL", 
            "Network": "Tailscale",
            "Status": "Remote"
        }
    }
    
    st.json(config_info)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🌐 Distributed Database System | Connected via Tailscale | 
        <a href="https://github.com/deepankar-MT24031/iia_test" target="_blank">GitHub Repository</a></p>
    </div>
    """,
    unsafe_allow_html=True
)
