# from flask import jsonify, current_app
# from sqlalchemy import func

# from models.models import Movie


# @bp.route("/film/<movie_id>", methods="GET")
# def get_film(movie_id):
#     item = Movie.query.filter_by(movieId=movie_id).first()
#     return jsonify(item.serialize)

