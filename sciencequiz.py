from flask import Flask, render_template, request, redirect
from model import *
from db import *

DEBUG = True

app = Flask(__name__)


@app.route('/')
def science_quiz():
    return render_template('main.html', title="ScienceQuiz")


@app.route('/manage')
def manage():
    return render_template('manage/manage.html')


@app.route('/manage/questions')
def manage_questions():
    return render_template('manage/questions.html', categories=fetch_all_categories())


@app.route('/manage/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        print(type(request.form['newcategory']))
        db.execute("INSERT INTO categories (name) VALUES (%s)", (request.form['newcategory'],), True)
    return render_template('manage/categories.html', categories=fetch_all_categories())


# TODO: CSRF or so...
@app.route('/manage/category/<category>', methods=['POST'])
def delete_category(category):
    if 'delete' in request.form:
        category = int(category)
        db.execute("DELETE FROM categories WHERE id=(%s)", (category,), True)
    return redirect('/manage/categories')


# TODO: Correct answer + guess question
@app.route('/manage/questions/new', methods=['GET', 'POST'])
def manage_questions_new():
    if request.method == 'POST' and request.form['ansA'].strip() and request.form['ansB'].strip() and \
            request.form['ansC'].strip() and request.form['ansD'].strip():
        question = db.execute("INSERT INTO questions (question, category) VALUES (%s, %s)",
                              (request.form['question'], request.form['category']), True)
        db.execute("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                   (question, request.form['ansA'].strip(), False), True)
        db.execute("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                   (question, request.form['ansB'].strip(), False), True)
        db.execute("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                   (question, request.form['ansC'].strip(), False), True)
        db.execute("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                   (question, request.form['ansD'].strip(), False), True)
    return render_template('manage/questions_new.html', categories=fetch_all_categories())


def fetch_all_categories():
    res = db.execute("SELECT * FROM categories")
    categories = []
    for r in res:
        categories.append(Category(*r, db=db))
    return categories


if __name__ == '__main__':
    global DEBUG, db
    db = PGSQLConnection(database="scq", user="scq", password="scq", host="localhost", port=5433)
    app.debug = DEBUG
    app.run(threaded=True)
