from flask import Flask, render_template, request, redirect
import psycopg2
import psycopg2.extensions
import logging
from model import *

DEBUG = True


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
        print(args)
        logger.info(self.mogrify(sql, args))

        try:
            psycopg2.extensions.cursor.execute(self, sql, args)
        except Exception as exc:
            logger.error("%s: %s" % (exc.__class__.__name__, exc))
            raise


app = Flask(__name__)


@app.route('/')
def science_quiz():
    return render_template('main.html', title="ScienceQuiz")


@app.route('/manage')
def manage():
    return render_template('manage/manage.html')


@app.route('/manage/questions')
def manage_questions():
    res = db_exec("SELECT * FROM questions LIMIT 10")
    print(res)
    return render_template('manage/questions.html')


@app.route('/manage/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        print(type(request.form['newcategory']))
        db_exec("INSERT INTO categories (name) VALUES (%s)", (request.form['newcategory'],), True)
    return render_template('manage/categories.html', categories=fetch_all_categories())


# TODO: CSRF or so...
@app.route('/manage/category/<category>', methods=['POST'])
def delete_category(category):
    if 'delete' in request.form:
        category = int(category)
        db_exec("DELETE FROM categories WHERE id=(%s)", (category,), True)
    return redirect('/manage/categories')


# TODO: Correct answer + guess question
@app.route('/manage/questions/new', methods=['GET', 'POST'])
def manage_questions_new():
    if request.method == 'POST' and request.form['ansA'].strip() and request.form['ansB'].strip() and \
            request.form['ansC'].strip() and request.form['ansD'].strip():
        question = db_exec("INSERT INTO questions (question, category) VALUES (%s, %s)",
                           (request.form['question'], request.form['category']), True)
        db_exec("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                (question, request.form['ansA'].strip(), False), True)
        db_exec("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                (question, request.form['ansB'].strip(), False), True)
        db_exec("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                (question, request.form['ansC'].strip(), False), True)
        db_exec("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                (question, request.form['ansD'].strip(), False), True)
    return render_template('manage/questions_new.html', categories=fetch_all_categories())


def db_exec(query, params=None, insert=False):
    if DEBUG:
        cur = conn.cursor(cursor_factory=LoggingCursor)
    else:
        cur = conn.cursor()
    if insert:
        query += ' RETURNING id'
    cur.execute(query, params)
    if insert:
        res = cur.fetchone()[0]
        cur.close()
        return res
    res = cur.fetchall()
    cur.close()
    return res


def fetch_all_categories():
    res = db_exec("SELECT * FROM categories")
    categories = []
    for r in res:
        categories.append(Category(*r))
    return categories


if __name__ == '__main__':
    global DEBUG
    conn = psycopg2.connect(database="scq", user="scq", password="scq", host="127.0.0.1", port=5433)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    app.debug = DEBUG
    app.run(threaded=True)
