from flask import Flask, render_template, redirect, request, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, FloatField
from flask_sqlalchemy import SQLAlchemy
import requests
import urllib.parse
import os

api_key = os.environ.get("API_KEY")
image_url = 'https://image.tmdb.org/t/p/w500/'


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
db = SQLAlchemy(app)
app.secret_key = 'pythonnormiecoder'


class MovieForm(FlaskForm):
    rating = FloatField(label='Your Rating Out of 10')
    review = StringField(label='Your Review Please')
    submit = SubmitField(label='Done')


class Add_movie(FlaskForm):
    name = StringField(label='Enter Movie Name')
    submit = SubmitField(label='Search')


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year =  db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), unique=True, nullable=False)

    # def __repr__(self):
    #     return f'<Movie{self.id, self.title, self.year, self.description, self.rating, self.ranking, self.review, self.img_url}'


with app.app_context():
    db.create_all()
    # adding movie in database
    # new_movie = Movie(title='ZNMD',
    #                   year=2002,
    #                   description='good movie',
    #                   rating=6.5,
    #                   ranking=10,
    #                   review='good movie',
    #                   img_url='hhttshhjj')
    # db.session.add(new_movie)
    # db.session.commit()


@app.route('/')
def index():
    movie = db.session.query(Movie).all()
    return render_template('index.html', movies=movie)


@app.route('/update', methods=['GET', 'POST'])
def update():
    movie_form = MovieForm()
    if request.method == 'POST':
        movie_id = request.args.get('id')
        movie_update = Movie.query.get(movie_id)
        movie_update.rating = movie_form.rating.data
        movie_update.review = movie_form.review.data
        db.session.commit()
        return redirect(url_for('index'))
    movie_id = request.args.get('id')
    print(movie_id)
    movie_selected = Movie.query.get(movie_id)
    return render_template('form.html', form=movie_form, mid=movie_selected)

@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    delete_movie = Movie.query.get(movie_id)
    db.session.delete(delete_movie)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    add_movie = Add_movie()
    if request.method == 'POST':
        count = 0
        query_param = add_movie.name.data
        encoded_query_param = urllib.parse.quote_plus(query_param.title())
        url = f'https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={encoded_query_param}'
        response = requests.get(url)
        data = response.json()
        movie_data = data['results']
        for d in movie_data:
            print(d['original_title'])
        return render_template('movie_results.html', results=movie_data, index=count)
    return render_template('add_movie.html', form=add_movie)


@app.route('/home')
def add_in_database():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_api_id}?api_key={api_key}')
        data = response.json()
        print(data)
        new_movie = Movie(
            title=data["original_title"],
            year=data["release_date"].split('-')[0],
            img_url=f"{image_url}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

