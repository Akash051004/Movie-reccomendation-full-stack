from flask import Flask, render_template, request
import pandas as pd
import pickle
import requests

app = Flask(__name__)

# 1. Load the data exactly as it was structured in your notebook
# The dictionary was created from 'movies' which has a 'movie_id' column
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
movie_list = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


def fetch_poster(movie_id):
    # Your TMDB API Key
    api_key = "8a75addc7995bce3e77bda169e15e128"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        # Poster path from TMDB
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    except:
        # Fallback if poster is missing
        return "https://via.placeholder.com/500x750?text=Poster+Not+Found"


@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    selected_movie_name = None

    if request.method == "POST":
        movie_title = request.form.get("movie_name")

        # Check if the movie exists in our list
        if movie_title in movies['title_x'].values:
            selected_movie_name = movie_title

            # Find the index of the movie
            idx = movies[movies['title_x'] == movie_title].index[0]

            # Get similarity scores and sort them
            distances = sorted(
                list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])[1:7]

            for i in distances:
                # --- FIXED LINE: Using 'movie_id' instead of 'id' ---
                m_id = movies.iloc[i[0]]['movie_id']

                recommendations.append({
                    "title": movies.iloc[i[0]]['title_x'],
                    "poster": fetch_poster(m_id)
                })

    return render_template("index.html",
                           movie_names=movie_list,
                           recommendations=recommendations,
                           selected_movie=selected_movie_name)


if __name__ == "__main__":
    app.run(debug=True)
