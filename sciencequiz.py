from flask import Flask, render_template, request
import psycopg2
import psycopg2.extensions
import logging
from model import *

DEBUG = True


class LoggingCursor(psycopg2.extensions.cursor):
    def execute(self, sql, args=None):
        logger = logging.getLogger('sql_debug')
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


@app.route('/manage/categories')
def manage_categories():
    return render_template('manage/categories.html', categories=fetch_all_categories())


@app.route('/manage/questions/new', methods=['GET', 'POST'])
def manage_questions_new():
    if request.method == 'POST':
        db_exec("INSERT INTO questions (question, category) VALUES (%s, %s)",
                (request.form['question'], request.form['category']), True)
    return render_template('manage/questions_new.html', categories=fetch_all_categories())


def db_exec(query, params=None, insert=False):
    if DEBUG:
        cur = conn.cursor(cursor_factory=LoggingCursor)
    else:
        cur = conn.cursor()
    cur.execute(query, params)
    if insert:
        cur.close()
        return
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
