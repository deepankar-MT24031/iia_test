import streamlit as st
import asyncio

# Page config
st.set_page_config(
    page_title="BingeBox - Database Mediation",
    page_icon="🎬",
    layout="wide"
)

# CSS for the layout matching your wireframe
st.markdown("""
<style>
.stApp {background: #ffffff; color: #333333;}
.main-header {
    font-size: 2.5rem; 
    color: #e50914; 
    text-align: center; 
    margin-bottom: 2rem;
    padding: 1rem;
    border: 2px solid #333333;
    background-color: #f8f9fa;
}
.custom-box {
    padding: 1.5rem;
    border: 2px solid #333333;
    margin: 1rem 0;
    background-color: #ffffff;
    min-height: 200px;
    display: flex;
    flex-direction: column;
}
.section-title {
    font-size: 1.2rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 1rem;
}
.filter-section { min-height: 200px; }
.chat-section { min-height: 200px; }
.mediation-section { min-height: 150px; }
.wrapper-section { min-height: 150px; }
.global-section { min-height: 200px; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "message": "Hi! I'm BingeBot. Ask me about movies, series, or database operations!"}
    ]
if "search_results" not in st.session_state:
    st.session_state.search_results = {"movies": [], "series": []}
if "last_search" not in st.session_state:
    st.session_state.last_search = ""

# HEADER - BINGEBOX
st.markdown('<div class="main-header">BINGEBOX</div>', unsafe_allow_html=True)

# TOP ROW: FILTER AREA AND CHAT BOT (Side by side)
top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    st.markdown('<div class="custom-box filter-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">FILTER AREA</div>', unsafe_allow_html=True)
    
    search_term = st.text_input("Search Term", placeholder="Enter movie or series name...", key="filter_search")
    
    col1, col2 = st.columns(2)
    with col1:
        include_movies = st.checkbox("Include Movies", value=True)
    with col2:
        include_series = st.checkbox("Include Series", value=True)
    
    if st.button("🔍 Search", key="search_filter", use_container_width=True):
        if search_term:
            st.session_state.last_search = search_term
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with top_col2:
    st.markdown('<div class="custom-box chat-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">CHAT BOT</div>', unsafe_allow_html=True)
    
    # Display chat messages in a container with limited height
    chat_container = st.container(height=150)
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["message"])
    
    st.markdown('</div>', unsafe_allow_html=True)

# MEDIATION SECTION (Full width)
st.markdown('<div class="custom-box mediation-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">MEDIATION WHERE THE QUERY FROM CHATBOT OR FILTER WILL SHOW</div>', unsafe_allow_html=True)

if st.session_state.last_search:
    st.info(f"🔄 Processing query: '{st.session_state.last_search}'")
    st.markdown("**Mediation layer is coordinating between Filter and Chat inputs, sending queries to both wrappers...**")
else:
    st.markdown("*Waiting for query from Filter Area or Chat Bot...*")

st.markdown('</div>', unsafe_allow_html=True)

# WRAPPER ROW (Side by side)
wrapper_col1, wrapper_col2 = st.columns([1, 1])

with wrapper_col1:
    st.markdown('<div class="custom-box wrapper-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">WRAPPER 1 QUERY WILL SHOW HERE</div>', unsafe_allow_html=True)
    
    if st.session_state.last_search:
        st.markdown("**Movies Database Results:**")
        if include_movies:
            movies = [
                {"title": f"Movie matching '{st.session_state.last_search}'", "year": 2023, "rating": 8.5},
                {"title": f"Another '{st.session_state.last_search}' Film", "year": 2022, "rating": 7.8}
            ]
            for movie in movies:
                st.markdown(f"🎬 **{movie['title']}** ({movie['year']}) - Rating: {movie['rating']}")
        else:
            st.markdown("*Movies not included in search*")
    else:
        st.markdown("*No query received yet*")
    
    st.markdown('</div>', unsafe_allow_html=True)

with wrapper_col2:
    st.markdown('<div class="custom-box wrapper-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">WRAPPER 2 QUERY WILL SHOW HERE</div>', unsafe_allow_html=True)
    
    if st.session_state.last_search:
        st.markdown("**TV Series Database Results:**")
        if include_series:
            series = [
                {"title": f"Series about '{st.session_state.last_search}'", "seasons": 4, "rating": 9.1},
                {"title": f"'{st.session_state.last_search}' Chronicles", "seasons": 2, "rating": 8.7}
            ]
            for s in series:
                st.markdown(f"📺 **{s['title']}** ({s['seasons']} seasons) - Rating: {s['rating']}")
        else:
            st.markdown("*Series not included in search*")
    else:
        st.markdown("*No query received yet*")
    
    st.markdown('</div>', unsafe_allow_html=True)

# GLOBAL SCHEMA VIEW (Full width)
st.markdown('<div class="custom-box global-section">', unsafe_allow_html=True)
st.markdown('<div class="section-title">GLOBAL SCHEMA VIEW AFTER QUERY RESULT COMES FROM BOTH WRAPPERS</div>', unsafe_allow_html=True)

if st.session_state.last_search:
    st.markdown("**Unified Results from Both Wrappers:**")
    
    # Combine results from both wrappers
    if include_movies:
        st.markdown("**Movies:**")
        st.markdown(f"🎬 Movie matching '{st.session_state.last_search}' (2023) - Rating: 8.5")
        st.markdown(f"🎬 Another '{st.session_state.last_search}' Film (2022) - Rating: 7.8")
    
    if include_series:
        st.markdown("**TV Series:**")
        st.markdown(f"📺 Series about '{st.session_state.last_search}' (4 seasons) - Rating: 9.1")
        st.markdown(f"📺 '{st.session_state.last_search}' Chronicles (2 seasons) - Rating: 8.7")
    
    st.success("✅ Global schema successfully merged results from both database wrappers")
else:
    st.markdown("*Global schema waiting for results from wrappers...*")

st.markdown('</div>', unsafe_allow_html=True)

# Chat input at the bottom (outside any containers)
if prompt := st.chat_input("💬 Ask BingeBot about movies, series, or database operations..."):
    # Add user message to chat history
    st.session_state.chat_messages.append({"role": "user", "message": prompt})
    
    # Generate bot response
    response = f"🔍 Searching for: '{prompt}' - Sending query to mediation layer..."
    st.session_state.chat_messages.append({"role": "assistant", "message": response})
    
    # Trigger search based on chat input
    st.session_state.last_search = prompt
    st.rerun()
