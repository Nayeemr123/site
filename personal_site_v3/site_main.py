import streamlit as st

# page setup
about_page =st.Page(
    page = "pages/about_me.py",
    title="About Me",
    icon="📧",
    default=True,
)

porfolio_performance =st.Page(
    page = "pages/porfolio_performance.py",
    title="Portfolio Performance Analyzer",
    icon="📈",
)

# Nav Bar
nav = st.navigation(
    {
        "Info": [about_page],
        "Projects": [porfolio_performance],
    }
)

nav.run()