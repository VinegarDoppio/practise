import os
from contextlib import closing

import jpype
import jaydebeapi


def get_conn():
    if jpype.isJVMStarted() and not jpype.isThreadAttachedToJVM():
        jpype.attachThreadToJVM()
        jpype.java.lang.Thread.currentThread().setContextClassLoader(
            jpype.java.lang.ClassLoader.getSystemClassLoader()
        )
    return jaydebeapi.connect(
        jclassname='org.postgresql.Driver',
        url='jdbc:postgresql://localhost:5432/dvdrental',
        driver_args={'user': 'postgres', 'password': 'postgres'},
        jars=os.path.join(os.path.dirname(__file__), 'postgresql-42.2.20.jar')
    )


def get_attribute_ids(cursor, category, language):
    cursor.execute(
        'select category_id from public.category where name = ? order by category_id limit 1',
        [category]
    )
    category_id = cursor.fetchone()[0]
    cursor.execute(
        'select language_id from public.language where name = ? order by language_id limit 1',
        [language]
    )
    language_id = cursor.fetchone()[0]
    return category_id, language_id


def get_categories(cursor=None):
    if cursor:
        cursor.execute('select distinct name from public.category order by name')
        return cursor.fetchall()
    with closing(get_conn()) as conn:
        with closing(conn.cursor()) as cursor:
            return get_categories(cursor)


def get_film_attributes():
    with closing(get_conn()) as conn:
        with closing(conn.cursor()) as cursor:
            categories = get_categories(cursor)
            cursor.execute('select distinct name from public.language order by name')
            languages = cursor.fetchall()
            return categories, languages


def get_films(category):
    sql = """
        select f.film_id,
        f.title,
        f.description,
        f.release_year,
        l.name as language,
        f.length,
        f.rating
        from public.film f
        join public.language l
        on f.language_id = l.language_id
        join public.film_category fc
        on f.film_id = fc.film_id
        join public.category c
        on fc.category_id = c.category_id
        where c.name = ?
        order by f.title
    """
    with closing(get_conn()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(sql, [category])
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            categories = get_categories(cursor)
            return rows, columns, categories


def insert_film(title, description, category, release_year, language, length, rating):
    sql = """
        insert into public.film
        (film_id, title, description, release_year, language_id, length, rating)
        values (?, ?, ?, ?::year, ?, ?, ?::mpaa_rating)
    """
    with closing(get_conn()) as conn:
        with closing(conn.cursor()) as cursor:
            category_id, language_id = get_attribute_ids(cursor, category, language)
            cursor.execute('select max(film_id) from public.film')
            max_film_id = cursor.fetchone()[0]
            film_id = int(max_film_id) + 1
            cursor.execute(
                sql,
                [film_id, title, description, release_year, language_id, length, rating]
            )
            cursor.execute(
                'insert into public.film_category (film_id, category_id) values (?, ?)',
                [film_id, int(category_id)]
            )


def update_film(
        film_id,
        title,
        description,
        category,
        release_year,
        language,
        length,
        rating
    ):
    sql = """
        update public.film set
        title = ?,
        description = ?,
        release_year = ?::year,
        language_id = ?,
        length = ?,
        rating = ?::mpaa_rating
        where film_id = ?
    """
    with closing(get_conn()) as conn:
        with closing(conn.cursor()) as cursor:
            category_id, language_id = get_attribute_ids(cursor, category, language)
            cursor.execute(
                sql,
                [title, description, release_year, language_id, length, rating, film_id]
            )
            cursor.execute(
                'update public.film_category set category_id = ? where film_id = ?',
                [category_id, film_id]
            )


def delete_film(film_id):
    sql = """
        select rental_id from public.rental
        where inventory_id in (select inventory_id from public.inventory where film_id = ?)
    """
    with closing(get_conn()) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(sql, [film_id])
            rental_ids = cursor.fetchall()
            print('Performing cascade delete...')
            cursor.executemany('delete from public.payment where rental_id = ?', rental_ids)
            print(cursor.rowcount, 'row(s) removed from public.payment')
            cursor.executemany('delete from public.rental where rental_id = ?', rental_ids)
            print(cursor.rowcount, 'row(s) removed from public.rental')
            cursor.execute('delete from public.inventory where film_id = ?', [film_id])
            print(cursor.rowcount, 'row(s) removed from public.inventory')
            cursor.execute('delete from public.film_actor where film_id = ?', [film_id])
            print(cursor.rowcount, 'row(s) removed from public.film_actor')
            cursor.execute('delete from public.film_category where film_id = ?', [film_id])
            print(cursor.rowcount, 'row(s) removed from public.film_category')
            cursor.execute('delete from public.film where film_id = ?', [film_id])
            print(cursor.rowcount, 'row(s) removed from public.film')
