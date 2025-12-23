import os
import requests
import pickle
import pandas as pd
import streamlit as st

# ---------- Google Drive download ----------
def download_from_drive(url, filename):
    if os.path.exists(filename):
        return

    st.write(f"Downloading {filename}...")
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)
    st.write(f"{filename} downloaded successfully.")

MOVIE_DICT_URL = "https://drive.google.com/uc?export=download&id=1oGCSRzQb9rQksmgPrm6WrCkhoHPhBc3P"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1-R_LVjqm4RPr-j1XT0U9PAnX7_JI1Pbx"

download_from_drive(MOVIE_DICT_URL, "movie_dict.pkl")
download_from_drive(SIMILARITY_URL, "similarity.pkl")

# ---------- Load data ----------
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------- Recommendation logic ----------
def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=6bcf4176dd5a400c1f5c569989ff31e6&language=en-US"
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]

def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# ---------- Streamlit UI ----------
st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie:",
    movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)
