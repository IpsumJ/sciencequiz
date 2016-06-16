from flask import Flask, render_template, request, redirect
from flask.ext.socketio import SocketIO, emit
from model import *
from db import *
from beaker.middleware import SessionMiddleware

# TODO!!!: Error handling
DEBUG = True

session_opts = {
    'session.type': 'file',
    'session.url': '127.0.0.1:5000',
    'session.data_dir': './cache',
}

app = Flask(__name__)
socketio = SocketIO(app)


@app.context_processor
def inject_user():
    s = request.environ['beaker.session']
    u = None
    if 'login' in s:
        u = s['login']
    return dict(user=u)


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
        db.execute("DELETE FROM categories WHERE id=(%s)", (category,), None)
    return redirect('/manage/categories')


# TODO: guess question
@app.route('/manage/questions/new', methods=['GET', 'POST'])
def manage_questions_new():
    if request.method == 'POST' and request.form['ansA'].strip() and request.form['ansB'].strip() and \
            request.form['ansC'].strip() and request.form['ansD'].strip():
        question = db.execute("INSERT INTO questions (question, category) VALUES (%s, %s)",
                              (request.form['question'], request.form['category']), True)
        correct = request.form['correct']
        db.execute("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                   (question, request.form['ansA'].strip(), correct == 'a'), True)
        db.execute("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                   (question, request.form['ansB'].strip(), correct == 'b'), True)
        db.execute("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                   (question, request.form['ansC'].strip(), correct == 'c'), True)
        db.execute("INSERT INTO answers (answers, answer, correct) VALUES (%s, %s, %s)",
                   (question, request.form['ansD'].strip(), correct == 'd'), True)
        return redirect('/manage/questions/new')
    return render_template('manage/questions_new.html', categories=fetch_all_categories())


@app.route('/manage/question/<question>/edit', methods=['GET', 'POST'])
def edit_question(question):
    question = int(question)
    if request.method == 'POST':
        if 'delete' in request.form:
            db.execute("DELETE questions WHERE id = %s", (question,), None)
            return redirect('/manage/questions')

        correct = request.form['correct']
        db.execute("UPDATE questions SET question = %s, category = %s WHERE id = %s",
                   (request.form['question'], request.form['category'], question), True)
        db.execute("UPDATE answers set answer = %s, correct = %s WHERE id=%s",
                   (request.form['ansA'].strip(), correct == 'a', request.form['aid']), True)
        db.execute("UPDATE answers set answer = %s, correct = %s WHERE id=%s",
                   (request.form['ansB'].strip(), correct == 'b', request.form['bid']), True)
        db.execute("UPDATE answers set answer = %s, correct = %s WHERE id=%s",
                   (request.form['ansC'].strip(), correct == 'c', request.form['cid']), True)
        db.execute("UPDATE answers set answer = %s, correct = %s WHERE id=%s",
                   (request.form['ansD'].strip(), correct == 'd', request.form['did']), True)

        return redirect('/manage/question/{}/edit'.format(question))
    return render_template('manage/questions_new.html', q=Question.get_by_id(question, db),
                           categories=fetch_all_categories())


@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    return render_template('try.html')


@socketio.on('connect', namespace='/quiz')
def quiz_connect():
    emit('question', {'question': 'Connected', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd'})

    print("Connected")


@socketio.on('answer_selected', namespace='/quiz')
def answer_selected(message):
    ans = message['sel']
    #answer is correct, do something
    if ans == 'c':
        pass

    emit('answer_response', {'correct': 'c'})


def fetch_all_categories():
    res = db.execute("SELECT * FROM categories")
    categories = []
    for r in res:
        categories.append(Category(**r, db=db))
    return categories


if __name__ == '__main__':
    global DEBUG, db
    db = PGSQLConnection(database="scq", user="scq", password="scq", host="localhost", port=5433)
    app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
    app.debug = DEBUG
    app.run(threaded=True)
