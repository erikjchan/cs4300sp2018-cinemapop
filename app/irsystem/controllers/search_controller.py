from . import *
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
import json
import user_duration
import user_release
from random import *

net_ids = ["Angela Zhang: az337", "Chris Fifty: cjf92", "Newton Ni: cn279", "Erik Chan: ejc233", "Xinyu Zhao: xz293"]

movies_json = json.load(open('app/static/data/movies.json'))
genres_json = json.load(open('genres.json'))
movie_list = [movie['title'] for movie in movies_json]
genre_list = [genre['name'] for genre in genres_json['genres']]

year_lst = []
for x in range(1900,2019):
    year_lst.append(x)

@irsystem.route('/', methods=['GET'])
def search():
    output_message = ""
    data = []
    movies_json = json.load(open('app/static/data/movies.json'))
    genres_json = json.load(open('genres.json'))
    movie_list = [movie['title'] for movie in movies_json]
    genre_list = [genre['name'] for genre in genres_json['genres']]

    similar = request.args.get('similar')
    genres = request.args.get('genres')
    release = request.args.get('release')
    acclaim = request.args.get('acclaim')
    castCrew = request.args.get('castCrew')
    keywords = request.args.get('keywords')
    duration = request.args.get('duration')
    year_range = [request.args.get('year_start'), request.args.get('year_end')]
    query = [similar, genres, duration, release, acclaim, castCrew, keywords]
    if not query[0] and not query[1] and not query[2] and not query[3] and not query[4] and not query[5] and not query[6]:
        data = []
        output_message = ''
    else:
        selected_movies = parse_lst_str(similar)
        selected_genres = parse_lst_str(genres)
        selected_crew = parse_lst_str(castCrew)
        selected_keywords = parse_lst_str(keywords)

        data = []
        movie_dict = dict()
        score_dict = dict()

        for movie in movies_json:
            movie_dict[movie['id']] = json.load(open('app/static/data/movies/' + movie['id'] + '.json'))
            score_dict[movie['id']] = 0.0

        # modify movie_dict and score_dict to account for the "duration" user input
        # assuming duration is in the form "90-180" rather than "180 - 90"
        if duration:
            movie_dict, score_dict = user_duration.main(movie_dict,score_dict,duration,10,0)
        if release:
            movie_dict, score_dict = user_release.main(movie_dict,score_dict,release,4,0)

        for movie in score_dict:
            if genres and genres in set(movie_dict[movie]['genres']):
                score_dict[movie] += 20.0
            if acclaim == "yes":
                if movie_dict[movie]['tmdb_score_value'] > 7.0:
                    score_dict[movie] += movie_dict[movie]['tmdb_score_value'] + 10.0
                if movie_dict[movie]['tmdb_score_value'] < 7.0:
                    score_dict[movie] -= 100.0

        sorted_score_dict = sorted(score_dict.iteritems(), key=lambda (k,v): (v,k), reverse=True)[:20]

        for movie_tuple in sorted_score_dict:
            movie_id, movie_score = movie_tuple
            movie_dict[movie_id]['similarity'] = movie_score
            data.append(movie_dict[movie_id])

        output_message = "Your search has been processed."

    return render_template('search.html', netids=net_ids, output_message=output_message, data=data, movie_list=movie_list, genre_list=genre_list, year_list= year_lst)

def parse_lst_str(lst_str):
        parsed = []
        if lst_str:
            lst_str = lst_str.encode('ascii', 'ignore')
            if ';' in lst_str:
                parsed = lst_str.split(";")
            for ind in range(0, len(parsed)):
                parsed[ind] = parsed[ind].lower().strip()
        return parsed
