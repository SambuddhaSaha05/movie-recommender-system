import os
import requests
import pickle
import pandas as pd
import streamlit as st

# ---------------- DOWNLOAD FROM GOOGLE DRIVE ---------------- #

def download_from_drive(file_id, filename):
    if os.path.exists(filename):
        return

    st.write(f"Downloading {filename}...")

    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': file_id}, stream=True)

    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            params = {'id': file_id, 'confirm': value}
            response = session.get(URL, params=params, stream=True)

    with open(filename, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

    st.success(f"{filename} downloaded successfully.")

# ---------------- GOOGLE DRIVE FILE IDS ---------------- #

MOVIE_DICT_ID = "1oGCSRzQb9rQksmgPrm6WrCkhoHPhBc3P"
SIMILARITY_ID = "1-R_LVjqm4RPr-j1XT0U9PAnX7_JI1Pbx"

download_from_drive(MOVIE_DICT_ID, "movie_dict.pkl")
download_from_drive(SIMILARITY_ID, "similarity.pkl")

# ---------------- LOAD DATA ---------------- #

movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- MOVIE POSTER FUNCTION ---------------- #

def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=6bcf4176dd5a400c1f5c569989ff31e6&language=en-US"
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]

# ---------------- RECOMMENDATION FUNCTION ---------------- #

def recommend(movie):
    movie_index = movies[movies["title"] == movie].index[0]
    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)), reverse=True, key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# ---------------- STREAMLIT UI ---------------- #

st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie:", movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])
