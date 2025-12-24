import os
import requests
import pickle
import pandas as pd

def download_from_drive(url, filename):
    if os.path.exists(filename):
        return

    r = requests.get(url, stream=True)
    if "text/html" in r.headers.get("Content-Type", ""):
        raise ValueError(f"{filename} is corrupted or HTML page downloaded.")

    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)

MOVIE_DICT_URL = "https://drive.google.com/uc?export=download&id=1oGCSRzQb9rQksmgPrm6WrCkhoHPhBc3P"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1-R_LVjqm4RPr-j1XT0U9PAnX7_JI1Pbx"

download_from_drive(MOVIE_DICT_URL, "movie_dict.pkl")
download_from_drive(SIMILARITY_URL, "similarity.pkl")

movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))


# --------- FUNCTIONS ----------

def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=6bcf4176dd5a400c1f5c569989ff31e6&language=en-US"
    )
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]

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

# --------- UI ----------

st.title("Movie Recommender System")

selected_movie_name = st.selectbox("Select a movie:", movies["title"].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
