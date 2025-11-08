import streamlit as st
from sympy.codegen.cnodes import sizeof

from agents.movies_agent import get_movies_recommendations
from config.config import tmdb_regions, TMDB_IMAGE_BASE_URL
from tmdb_services.tmdb_service import get_trending_movies

st.title("🎬 AI Movie Recommender")
st.write("Describe what you want to watch. We'll find movies and show where to watch them.")


# Sidebar
size = st.sidebar.slider("No. of suggestions",5,20,5)

selected_region = st.sidebar.selectbox(
    "🌍 Choose your region ",
    options=list(tmdb_regions.values()),
    index=1  # default selection (India)
)

st.sidebar.markdown("<b>Trending</b>",unsafe_allow_html=True)
trending_movies = get_trending_movies(selected_region)
movies=trending_movies.get("results")
for movie in movies:
    st.sidebar.image(f"{TMDB_IMAGE_BASE_URL}{movie['poster_path']}", width="stretch")
    st.sidebar.markdown(
            f"""
            <div style='text-align:center; margin-top:8px;'>
                <strong>{movie["title"]}</strong><br>                
                ⭐ {movie['vote_average']} / 10<br>
                <span style='color:gray; font-size:13px;'>Released: {movie['release_date']}</span>
            </div>
            """,
            unsafe_allow_html=True,
    )


# Main section
st.markdown(f"🌍 Region {selected_region}")
query = st.text_area("Your movie mood / preferences",max_chars=100,height=80)
if st.button("Suggest Movies") and query.strip():
    with st.spinner("Building TMDB query, fetching movies, re-ranking..."):
        movies = get_movies_recommendations(query, size)

    if not movies:
        st.warning("No matches found. Try adjusting your preferences.")
    else:
        for m in movies:
            c1, c2 = st.columns([1, 3], vertical_alignment="top")

            with c1:
                if m.get("poster_url"):
                    st.image(m["poster_url"], use_container_width=True)

            with c2:
                year = (m.get("release_date") or "")[:4]
                st.subheader(f"{m['title']} {f'({year})' if year else ''}")
                st.caption(
                    f"⭐ {m.get('vote_average', 'N/A')}  |  {', '.join(m.get('genres', []))}"
                )
                st.write(m.get("overview") or "No overview available.")

                wp = m.get("where_to_watch", {})
                line_parts = []
                if wp.get("stream"):
                    line_parts.append("**Stream:** " + ", ".join(wp["stream"]))
                if wp.get("rent"):
                    line_parts.append("**Rent:** " + ", ".join(wp["rent"]))
                if wp.get("buy"):
                    line_parts.append("**Buy:** " + ", ".join(wp["buy"]))

                if line_parts:
                    st.markdown(" | ".join(line_parts))
                elif wp.get("fallback_url"):
                    st.markdown(f"[Find where to watch]({wp['fallback_url']})")

            st.markdown("---")

