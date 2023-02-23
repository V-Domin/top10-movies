from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests




app = Flask(__name__)
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
API_KEY = '41a44541a1abc8ee30fda23d6e386ecf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///top-ten-movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)



## EDIT FORM
class EditForm(FlaskForm):
    rating = StringField("Your rating out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField('Add Movie')

## CREATE DB
with app.app_context():
    class Movie(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(30), unique=True, nullable=True)
        year = db.Column(db.Integer, nullable=True)
        description = db.Column(db.String(500), nullable=True)
        rating = db.Column(db.Float, nullable=True)
        ranking = db.Column(db.Integer, nullable=True)
        review = db.Column(db.String(70), nullable=True)
        img_url = db.Column(db.String(250), nullable=True)

        def __repr__(self):
            return f'<Movie {self.title}>'

    db.create_all()

    # new_movie = Movie(
    #     title="Phone Booth",
    #     year=2002,
    #     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    #     rating=7.3,
    #     ranking=10,
    #     review="My favourite character was the caller.",
    #     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    #
    # db.session.add(new_movie)
    # db.session.commit()

    # all_movies = db.session.query(Movie).all()

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/edit', methods=['POST', 'GET'])
def edit():
    form = EditForm()

    movie_id = request.args.get('id')
    selected_movie = Movie.query.get(movie_id)

    if form.validate_on_submit():
        rating = form.rating.data
        review = form.review.data
        selected_movie.rating = rating
        selected_movie.review = review
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", form=form, movie=selected_movie)


@app.route("/delete", methods=['POST', 'GET'])
def delete():
    movie_id = request.args.get('id')
    selected_movie = Movie.query.get(movie_id)
    db.session.delete(selected_movie)
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/add", methods=['POST', 'GET'])
def add():
    form = AddForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        URL = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}'
        response = requests.get(URL)
        data = response.json()['results']
        return render_template('select.html', movies=data)

    return render_template('add.html', form=form)


@app.route("/find", methods=['POST', 'GET'])
def find():
    movie_id = request.args.get('id')
    if movie_id:
        URL = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}'
        response = requests.get(URL)
        data = response.json()
        title = data['title']
        year = data["release_date"].split("-")[0]
        img_url = f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}"
        description = data["overview"]
        new_movie = Movie(title=title, year=year, description=description, img_url=img_url)
        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
