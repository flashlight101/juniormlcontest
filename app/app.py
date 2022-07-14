from platform import release
from flask import Flask, jsonify, make_response

from flask_sqlalchemy import SQLAlchemy

from models.models import Movie, Rating, Links, engine
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from implicit.nearest_neighbours import CosineRecommender
from threading import Thread
import time

import pandas as pd

from tools import get_coo_matrix, generate_implicit_recs_mapper
app = Flask(__name__)

app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql://az_user:az_psw@db:5432/az_dbname"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['JSON_AS_ASCII'] = False
db = SQLAlchemy(app)

db_session = scoped_session(sessionmaker(bind=engine))
@app.route("/film/<movie_id>/<user_id>", methods=["GET"])
def get_film(movie_id,user_id):
    item = db_session.query(Movie).filter_by(movieid=movie_id).first()
    stars = db_session.query(Rating).filter_by(movieId=movie_id, userId=user_id).first()
    if stars is not None:
        stars = stars.rating
    return jsonify(
        original_title=item.original_title,
        ru_title=item.ru_title,
        kinopoisk_rating=item.kinopoisk_rating,
        imdb_rating=item.imdb_rating,
        description=item.description,
        image_link=item.image_link,
        year=item.year,
        country=item.country,
        genres=item.genres_x,
        producer=item.producer,
        scenario=item.scenario,
        release_date=item.release_date,
        age=item.age,
        duration=item.duration,
        stars=stars
        )

@app.route("/get_reccomend/<user_id>", methods=["GET"])
def get_rec(user_id):
    items = engine.execute("select recommendations.\"movieId\", movies.original_title,\
        movies.image_link from recommendations join public.movies\
        on recommendations.\"movieId\" = movies.movieId\
        where recommendations.\"userId\"={user_id}".format(user_id=user_id)).fetchall()
    
    return jsonify(json_list = [(item.movieId, item.original_title, item.image_link) for item in items])

@app.route("/post_stars", methods=["POST"])
def add_stars():
    data = request.get_json()

    new_rating = Rating(
        userId = data['userId'],
        movieId = data['movieId'],
        rating = data['rating'],
        timestamp = data['timestamp']
    )

    db.session.add(new_rating)
    db.session.commit()

def train():
    ratings = pd.read_sql_query('select * from ratings',con=engine)

    users_inv_mapping = dict(enumerate(ratings['userId'].unique()))
    users_mapping = {v: k for k, v in users_inv_mapping.items()}

    items_inv_mapping = dict(enumerate(ratings['movieId'].unique()))
    items_mapping = {v: k for k, v in items_inv_mapping.items()}

    train_mat = get_coo_matrix(
        ratings,
        users_mapping=users_mapping,
        items_mapping=items_mapping,
    ).tocsr()

    model = CosineRecommender(K=10)
    model.fit(train_mat.T, show_progress=False) 

    mapper = generate_implicit_recs_mapper( 
        model,
        train_mat,
        10,
        users_mapping,
        items_inv_mapping,
        filter_already_liked_items=True
    )

    recs = pd.DataFrame({'userId': ratings['userId'].unique()})
    recs['movieId'] = recs['userId'].map(mapper)
    recs = recs.explode('movieId')
    recs.movieId = recs.movieId.astype(int)
    recs.userId = recs.userId.astype(int)
    recs.to_sql('recommendations', engine, if_exists='replace', chunksize=10000)
def cache():
    while True:
        time.sleep(100000)
        train()
        
        

thread = Thread(target=cache)
thread.start()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")