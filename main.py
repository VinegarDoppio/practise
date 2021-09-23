from flask import Flask, request, flash, redirect, render_template
import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysupersecretkey'

film_ratings = ['G', 'PG', 'PG-13', 'R', 'NC-17']


def get_films_page(category):
    rows, columns, categories = db.get_films(category)
    film_category = category
    if category.endswith('s'):
        category = category[:-1]
    title = category + ' Films'
    return render_template(
        'films.html',
        title=title,
        rows=rows,
        columns=columns,
        categories=categories,
        film_category=film_category
    )


@app.route('/')
@app.route('/home')
@app.route('/index')
def show_home_page():
    categories = db.get_categories()
    return render_template('index.html', title='Welcome to Film Catalog', categories=categories)


@app.route('/action')
def show_action_films_page():
    return get_films_page('Action')


@app.route('/animation')
def show_animation_films_page():
    return get_films_page('Animation')


@app.route('/children')
def show_children_films_page():
    return get_films_page('Children')


@app.route('/classics')
def show_classic_films_page():
    return get_films_page('Classics')


@app.route('/comedy')
def show_comedy_films_page():
    return get_films_page('Comedy')


@app.route('/documentary')
def show_documentary_films_page():
    return get_films_page('Documentary')


@app.route('/drama')
def show_drama_films_page():
    return get_films_page('Drama')


@app.route('/family')
def show_family_films_page():
    return get_films_page('Family')


@app.route('/foreign')
def show_foreign_films_page():
    return get_films_page('Foreign')


@app.route('/games')
def show_game_films_page():
    return get_films_page('Games')


@app.route('/horror')
def show_horror_films_page():
    return get_films_page('Horror')


@app.route('/music')
def show_music_films_page():
    return get_films_page('Music')


@app.route('/new')
def show_new_films_page():
    return get_films_page('New')


@app.route('/sci-fi')
def show_scifi_films_page():
    return get_films_page('Sci-Fi')


@app.route('/sports')
def show_sport_films_page():
    return get_films_page('Sports')


@app.route('/travel')
def show_travel_films_page():
    return get_films_page('Travel')


@app.route('/add_film', methods=['GET', 'POST'])
def add_film():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        release_year = int(request.form['release_year'])
        language = request.form['language']
        length = int(request.form['length'])
        rating = request.form['rating']
        db.insert_film(
            title, description, category, release_year, language, length, rating
        )
        flash(message='Film "{0}" added to category "{1}"'.format(title, category), category='info')
        return redirect('/' + category.lower())
    categories, languages = db.get_film_attributes()
    return render_template(
        'add_film.html',
        title='Add Film',
        categories=categories,
        languages=languages,
        film_ratings=film_ratings
    )


@app.route('/edit_film', methods=['GET', 'POST'])
def edit_film():
    if request.method == 'POST':
        film_id = int(request.form['film_id'])
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        release_year = int(request.form['release_year'])
        language = request.form['language']
        length = int(request.form['length'])
        rating = request.form['rating']
        db.update_film(
            film_id, title, description, category, release_year, language, length, rating
        )
        flash(message='Film "{0}" updated'.format(title), category='info')
        return redirect('/' + category.lower())
    categories, languages = db.get_film_attributes()
    return render_template(
        'edit_film.html',
        title='Edit Film',
        categories=categories,
        languages=languages,
        film_ratings=film_ratings
    )


@app.route('/delete_film')
def delete_film():
    film_id = request.args.get('film_id', type=int)
    title = request.args.get('title', type=str)
    category = request.args.get('film_category', type=str)
    db.delete_film(film_id)
    flash(message='Film "{0}" removed from category "{1}"'.format(title, category), category='info')
    return redirect('/' + category.lower())


if __name__ == '__main__':
    app.run(debug=True)
