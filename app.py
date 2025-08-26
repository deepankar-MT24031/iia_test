import streamlit as st
import asyncio

# Page config
st.set_page_config(
    page_title="BingeBox - Database Mediation",
    page_icon="🎬",
    layout="wide"
)

# CSS for light theme (no dark shades)
st.markdown("""
<style>
.stApp {background: #ffffff; color: #333333;}
.main-header {font-size: 3rem; color: #e50914; text-align: center; margin-bottom: 1rem;}
.custom-box {
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    background-color: #f9f9f9;
    color: #333333;
    border: 1px solid #e0e0e0;
}
.filter-box { height: 350px; }
.chatbot-box { height: 350px; display: flex; flex-direction: column; }
.chat-history-container { 
    flex: 1; 
    overflow-y: auto; 
    padding-bottom: 10px; 
    max-height: 200px;
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 5px;
}
.mediation-box { height: 350px; }
.wrapper-box { height: 300px; }
.global-schema-box { height: 400px; }
.chat-message {
    margin: 5px 0;
    padding: 5px;
}
.user-message {
    background-color: #e3f2fd;
    border-radius: 5px;
    padding: 8px;
    margin: 5px 0;
}
.bot-message {
    background-color: #f5f5f5;
    border-radius: 5px;
    padding: 8px;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "bot", "message": "Hi! I'm BingeBot. Ask me about movies, series, or database operations!"}
    ]
if "search_results" not in st.session_state:
    st.session_state.search_results = {"movies": [], "series": []}

# HEADER
st.markdown('<h1 class="main-header">🎬 BingeBox</h1>', unsafe_allow_html=True)

# TOP ROW: FILTER AREA AND CHAT BOT
top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    with st.container():
        st.markdown('<div class="custom-box filter-box">', unsafe_allow_html=True)
        st.markdown("### 🔍 Filter Area")
        search_term = st.text_input("Search Term", placeholder="Enter movie or series name...", key="filter_search")
        include_movies = st.checkbox("Include Movies", value=True)
        include_series = st.checkbox("Include Series", value=True)
        
        # Add search button for filter
        if st.button("Search", key="search_filter"):
            if search_term:
                # Trigger search results update
                st.session_state.last_search = search_term
        st.markdown('</div>', unsafe_allow_html=True)

with top_col2:
    with st.container():
        st.markdown('<div class="custom-box chatbot-box">', unsafe_allow_html=True)
        st.markdown("### 🤖 Chat Bot")
        
        # Chat history display
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
            for i, msg in enumerate(st.session_state.chat_messages):
                if msg["role"] == "bot":
                    st.markdown(f'<div class="bot-message">🤖 {msg["message"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="user-message">👤 {msg["message"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Chat input section
        chat_col1, chat_col2 = st.columns([4, 1])
        with chat_col1:
            chat_input = st.text_input("Ask BingeBot", placeholder="Ask about movies, series...", key="chat_input", label_visibility="collapsed")
        with chat_col2:
            send_clicked = st.button("Send", key="send_chat", use_container_width=True)
        
        # Handle chat input
        if send_clicked and chat_input.strip():
            # Add user message
            st.session_state.chat_messages.append({"role": "user", "message": chat_input})
            # Add bot response
            bot_response = f"Received your question: '{chat_input}'. Let me search for that information!"
            st.session_state.chat_messages.append({"role": "bot", "message": bot_response})
            # Trigger search based on chat input
            st.session_state.last_search = chat_input
            # Rerun to update display
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)

# MIDDLE ROW: MEDIATION (Query Results)
with st.container():
    st.markdown('<div class="custom-box mediation-box">', unsafe_allow_html=True)
    st.markdown("### 🔄 Mediation: Queries from Filter or Chatbot will appear here")
    
    # Show current search status
    if hasattr(st.session_state, 'last_search'):
        st.info(f"Last search: '{st.session_state.last_search}'")
        st.markdown("**Processing query and fetching results from wrappers...**")
    else:
        st.markdown("*No queries yet. Use the filter area or chat with BingeBot to start searching.*")
    
    st.markdown('</div>', unsafe_allow_html=True)

# UPDATE SEARCH RESULTS BASED ON FILTER OR CHAT
if search_term or hasattr(st.session_state, 'last_search'):
    current_search = search_term or getattr(st.session_state, 'last_search', '')
    if current_search:
        # Simulate database search results
        st.session_state.search_results["movies"] = [
            {"title": f"Movie matching '{current_search}'", "year": 2022, "genre": "Action", "rating": 8.5, "director": "Dir A"},
            {"title": f"Another Movie with '{current_search}'", "year": 2020, "genre": "Comedy", "rating": 7.2, "director": "Dir B"}
        ] if include_movies else []
        st.session_state.search_results["series"] = [
            {"title": f"Series about '{current_search}'", "seasons": 3, "genre": "Drama", "rating": 9.0, "network": "Netflix"},
            {"title": f"'{current_search}' TV Show", "seasons": 2, "genre": "Thriller", "rating": 8.1, "network": "HBO"}
        ] if include_series else []

# NEXT ROW: WRAPPER 1 AND WRAPPER 2
wrapper_col1, wrapper_col2 = st.columns(2)

with wrapper_col1:
    st.markdown('<div class="custom-box wrapper-box">', unsafe_allow_html=True)
    st.markdown("### 🎬 Wrapper 1: Movies")
    movies = st.session_state.search_results.get("movies", [])
    if movies:
        for movie in movies:
            st.markdown(f"- **{movie['title']}** ({movie['year']}) | Genre: {movie['genre']} | Rating: {movie['rating']}")
    else:
        st.markdown("*No movies found or movies not included in search.*")
    st.markdown('</div>', unsafe_allow_html=True)

with wrapper_col2:
    st.markdown('<div class="custom-box wrapper-box">', unsafe_allow_html=True)
    st.markdown("### 📺 Wrapper 2: Series")
    series = st.session_state.search_results.get("series", [])
    if series:
        for s in series:
            st.markdown(f"- **{s['title']}** | Seasons: {s['seasons']} | Genre: {s['genre']} | Rating: {s['rating']} | Network: {s['network']}")
    else:
        st.markdown("*No series found or series not included in search.*")
    st.markdown('</div>', unsafe_allow_html=True)

# BOTTOM ROW: GLOBAL SCHEMA VIEW
with st.container():
    st.markdown('<div class="custom-box global-schema-box">', unsafe_allow_html=True)
    st.markdown("### 🌐 Global Schema View (Merged results from both wrappers)")
    
    all_results = []
    for movie in st.session_state.search_results.get("movies", []):
        all_results.append(f"🎬 **{movie['title']}** ({movie['year']}) - {movie['genre']}")
    for series in st.session_state.search_results.get("series", []):
        all_results.append(f"📺 **{series['title']}** ({series['seasons']} seasons) - {series['genre']}")
    
    if all_results:
        for result in all_results:
            st.markdown(result)
    else:
        st.markdown("*No results to display. Start searching to see merged results.*")
    
    st.markdown('</div>', unsafe_allow_html=True)
