import streamlit as st
import time
import threading

# Function to simulate activity without refreshing the page
def keep_alive():
    while True:
        time.sleep(300)  # Simulate activity every 5 minutes
        st.write("", key=f"keep_alive_{time.time()}")  # Write an empty string to the app

# Start the background thread
if not st.session_state.get("keep_alive_thread_started", False):
    thread = threading.Thread(target=keep_alive, daemon=True)
    thread.start()
    st.session_state.keep_alive_thread_started = True  # Ensure the thread starts only once

# Your existing code
about_page = st.Page(
    page="pages/about_me.py",
    title="About Me",
    icon="📧",
    default=True,
)

portfolio_performance = st.Page(
    page="pages/portfolio_performance.py",  # Corrected file name
    title="Portfolio Performance Analyzer",
    icon="📈",
)

# Nav Bar
nav = st.navigation(
    {
        "Info": [about_page],
        "Projects": [portfolio_performance],  # Corrected variable name
    }
)

nav.run()
