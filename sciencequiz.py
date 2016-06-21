from flask import Flask, render_template, request, redirect
from flask.ext.socketio import SocketIO, emit, join_room, leave_room
from model import *
from db import *
from beaker.middleware import SessionMiddleware
import datetime
import uuid
import configparser

# TODO!!!: Error handling
DEBUG = True

active_displays = {}

session_opts = {
    'session.type': 'file',
    'session.url': '127.0.0.1:5000',
    'session.data_dir': './cache',
}

app = Flask(__name__)
socketio = SocketIO(app)


# CONTEXT PROCESSORS
@app.context_processor
def inject_user():
    s = request.environ['beaker.session']
    u = None
    if 'login' in s:
        u = s['login']
    return dict(user=u)


@app.context_processor
def inject_year():
    return dict(year=datetime.datetime.now().year)


@app.route('/')
def science_quiz():
    return render_template('main.html', title="ScienceQuiz")


# MANAGE PAGES

@app.route('/manage')
def manage():
    return render_template('manage/manage.html')


@app.route('/manage/questions')
def manage_questions():
    return render_template('manage/questions.html', categories=Category.fetch_all(db), quizes=Quiz.get_all(db))


@app.route('/manage/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        print(type(request.form['newcategory']))
        db.execute("INSERT INTO categories (name) VALUES (%s)", (request.form['newcategory'],), True)
    return render_template('manage/categories.html', categories=Category.fetch_all(db))


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
    return render_template('manage/questions_new.html', categories=Category.fetch_all(db))


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
                           categories=Category.fetch_all(db))


@app.route('/manage/run/<token>')
def run_display(token):
    res = db.execute("SELECT * FROM device_api_tokens WHERE token=%s", (token,))
    if len(res) > 0:
        s = request.environ['beaker.session']
        s['device_token'] = DeviceToken(**res[0], db=db)
        s.save()
        active_displays[token].ready = False
        return redirect('/quiz')


@app.route('/manage/displays')
def manage_displays():
    return render_template('/manage/displays.html', displays=active_displays)


@app.route('/manage/arrange/<quiz>', methods=['GET', 'POST'])
def manage_arrange_edit(quiz):
    if request.method == 'POST':
        db.execute("UPDATE quizes SET name=%s, year=%s, public=%s WHERE id=%s",
                   (request.form['name'], request.form['year'], request.form['public'], quiz), True)
        return redirect('/manage/arrange')
    return render_template('manage/arrange_new.html', q=Quiz.get_by_id(quiz, db))


@app.route('/manage/arrange/<quiz>/add', methods=['GET'])
def manage_arrange_question(quiz):
    Quiz.get_by_id(quiz, db=db).add(Question.get_by_id(db=db, id=request.args.get('id')))
    return redirect('/manage/questions')


@app.route('/manage/clients', methods=['GET', 'POST'])
def manage_arrange_device_tokens():
    if request.method == 'POST':
        db.execute("INSERT INTO device_api_tokens (description, token) VALUES(%s, %s)",
                   (request.form['newtoken'], str(uuid.uuid5(uuid.NAMESPACE_DNS, 'sciencequiz.de'))), True)
        return redirect('/manage/clients')
    return render_template('/manage/device_tokens.html', devices=DeviceToken.get_all(db))


@app.route('/manage/client/<device>', methods=['POST'])
def manage_edit_device_token(device):
    if 'delete' in request.form:
        db.execute("DELETE FROM device_api_tokens WHERE id=%s", (device,), None)
    return redirect('/manage/clients')


@app.route('/manage/arrange', methods=['GET', 'POST'])
def manage_arrange():
    if request.method == 'POST':
        db.execute("DELETE FROM quizes WHERE id=%s", (request.form['id']), None)
        return redirect("/manage/arrange")
    return render_template('manage/arrange.html',
                           questions=[Quiz(**q, db=db) for q in db.execute("SELECT * FROM quizes")],
                           displays=[d for d in active_displays.values() if d.ready])


@app.route('/manage/arrange/new', methods=['GET', 'POST'])
def manage_arrange_new():
    if request.method == 'POST':
        year = int(request.args.get('year', datetime.datetime.now().year))
        name = request.form['name']
        db.execute("INSERT INTO quizes (name, year, public) VALUES(%s, %s, %s)", (name, year, 'public' in request.form),
                   True)
        return redirect("/manage/arrange")
    return render_template('manage/arrange_new.html')


# USER PAGES
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'device_token' in request.environ['beaker.session']:
        return render_template('try.html')
    return redirect('/display')


@app.route('/clear_session')
def clear_session():
    request.environ['beaker.session'].delete()
    return redirect('/')


@app.route('/display', methods=['GET', 'POST'])
def display():
    if request.method == 'POST':
        res = db.execute("SELECT * FROM device_api_tokens WHERE token=%s", (request.form['token'],))
        if len(res) > 0:
            s = request.environ['beaker.session']
            s['device_token'] = DeviceToken(**res[0], db=db)
            s.save()
            return redirect('/quiz')
    return render_template('display_login.html')


# SOCKET.IO STUFF
@socketio.on('connect', namespace='/quiz')
def quiz_connect():
    # emit('question', {'question': 'Connected', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd'})
    s = request.environ['beaker.session']
    if 'device_token' in s:
        print("Device token detected!")
        join_room(s['device_token'].token)
        dev = s['device_token']
        if dev.token in active_displays and not active_displays[dev.token].ready:
            emit('question', {'question': 'Connected', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd'}, room=dev.token)
        else:
            active_displays[dev.token] = Display(dev)
        print(s['device_token'].name, 'was added as active screen.')
    print("Connected")


@socketio.on('disconnect', namespace='/quiz')
def quiz_disconnect():
    s = request.environ['beaker.session']['device_token']
    leave_room(s.token)
    del (active_displays[s.token])
    print('disconnect', s.name)
    pass


@socketio.on('answer_selected_result', namespace='/quiz')
def answer_selected(message):
    disp = active_displays[request.environ['beaker.session']['device_token'].token]
    if not disp.w:
        return
    ans = message['sel']
    # answer is correct, do something
    if ans == 'c':
        pass

    emit('answer_response', {'correct': 'c'}, room=disp.token.token)


@socketio.on('answer_selected', namespace='/quiz')
def answer_selected(message):
    disp = active_displays[request.environ['beaker.session']['device_token'].token]
    if not disp.w:
        return
    ans = message['sel']
    emit('selection', {'selected': ans}, room=disp.token.token)


if __name__ == '__main__':
    global DEBUG, db
    config = configparser.ConfigParser()
    config.read("sciencequiz.ini")
    db = PGSQLConnection(database=config.get('db', 'db'), user=config.get('db', 'user'),
                         password=config.get('db', 'password'), host=config.get('db', 'host'),
                         port=int(config.get('db', 'port')))
    app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)
    app.debug = DEBUG
    app.run(threaded=True, host=config.get('sciencequiz', 'host'), port=int(config.get('sciencequiz', 'port')))
