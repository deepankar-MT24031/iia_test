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
.filter-box, .chatbot-box, .mediation-box, .wrapper-box, .global-schema-box {
    padding: 1rem; border-radius: 10px; margin: 0.5rem 0; background-color: #f9f9f9; color: #333333;
    height: 350px; overflow-y: auto;
    border: 1px solid #e0e0e0;
}
.wrapper-box {height: 300px;}
.global-schema-box {height: 400px;}
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
    st.markdown('<div class="filter-box">### 🔍 Filter Area</div>', unsafe_allow_html=True)
    search_term = st.text_input("Search Term", placeholder="Enter movie or series name...", key="filter_search")
    include_movies = st.checkbox("Include Movies", value=True)
    include_series = st.checkbox("Include Series", value=True)

with top_col2:
    st.markdown('<div class="chatbot-box">### 🤖 Chat Bot</div>', unsafe_allow_html=True)
    
    # Create a placeholder for chat messages
    chat_history_container = st.empty()
    
    # Display initial chat messages in the placeholder
    with chat_history_container.container():
        for msg in st.session_state.chat_messages[-5:]:
            if msg["role"] == "bot":
                st.markdown(f'🤖 {msg["message"]}')
            else:
                st.markdown(f'👤 {msg["message"]}')

    chat_input = st.text_input("Ask BingeBot", placeholder="Ask about movies, series...", key="chat_input")
    
    if st.button("Send", key="send_chat") and chat_input:
        st.session_state.chat_messages.append({"role": "user", "message": chat_input})
        bot_response = f"Received your question: {chat_input}"
        st.session_state.chat_messages.append({"role": "bot", "message": bot_response})
        st.rerun()

# MIDDLE ROW: MEDIATION (Query Results)
st.markdown('<div class="mediation-box">### 🔄 Mediation: Queries from Filter or Chatbot will appear here</div>', unsafe_allow_html=True)

# PLACEHOLDER LOGIC: FILL SEARCH RESULTS BASED ON FILTER / CHAT
if search_term or chat_input:
    # Fake data for demonstration
    st.session_state.search_results["movies"] = [
        {"title": "Movie A", "year": 2022, "genre": "Action", "rating": 8.5, "director": "Dir A"},
        {"title": "Movie B", "year": 2020, "genre": "Comedy", "rating": 7.2, "director": "Dir B"}
    ] if include_movies else []
    st.session_state.search_results["series"] = [
        {"title": "Series X", "seasons": 3, "genre": "Drama", "rating": 9.0, "network": "Netflix"},
        {"title": "Series Y", "seasons": 2, "genre": "Thriller", "rating": 8.1, "network": "HBO"}
    ] if include_series else []

# NEXT ROW: WRAPPER 1 AND WRAPPER 2
wrapper_col1, wrapper_col2 = st.columns(2)

with wrapper_col1:
    st.markdown('<div class="wrapper-box">### 🎬 Wrapper 1: Movies</div>', unsafe_allow_html=True)
    for movie in st.session_state.search_results.get("movies", []):
        st.markdown(f"- {movie['title']} ({movie['year']}) | Genre: {movie['genre']} | Rating: {movie['rating']}")

with wrapper_col2:
    st.markdown('<div class="wrapper-box">### 📺 Wrapper 2: Series</div>', unsafe_allow_html=True)
    for series in st.session_state.search_results.get("series", []):
        st.markdown(f"- {series['title']} | Seasons: {series['seasons']} | Genre: {series['genre']} | Rating: {series['rating']} | Network: {series['network']}")

# BOTTOM ROW: GLOBAL SCHEMA VIEW
st.markdown('<div class="global-schema-box">### 🌐 Global Schema View (Merged results from both wrappers)</div>', unsafe_allow_html=True)
for movie in st.session_state.search_results.get("movies", []):
    st.markdown(f"🎬 {movie['title']} ({movie['year']})")
for series in st.session_state.search_results.get("series", []):
    st.markdown(f"📺 {series['title']} ({series['seasons']} seasons)")
