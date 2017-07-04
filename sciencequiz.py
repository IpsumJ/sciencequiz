from flask import Flask, render_template, request, redirect, g
from flask_socketio import SocketIO, emit, join_room, leave_room
from model import *
from db import *
from beaker.middleware import SessionMiddleware
import datetime
import uuid

# TODO!!!: Error handling

active_displays = {}

session_opts = {
    'session.type': 'file',
    'session.url': '127.0.0.1:5000',
    'session.data_dir': './cache',
}

app = Flask(__name__)
socketio = SocketIO(app)
app.config.from_pyfile('config.py')
app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)


def get_db_conn():
    if not hasattr(g, 'scq_pg_db_conn'):
        g.scq_pg_db_conn = PGSQLConnection(database=app.config.get('DB'), user=app.config.get('DB_USER'),
                                           password=app.config.get('DB_PASSWORD'), host=app.config.get('DB_HOST'),
                                           port=app.config.get('DB_PORT'))
    return g.scq_pg_db_conn


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
    return render_template('manage/questions.html', categories=Category.fetch_all(get_db_conn()),
                           quizes=Quiz.get_all(get_db_conn()), db=get_db_conn())


@app.route('/manage/teams')
def manage_teams():
    return render_template('manage/teams.html', teams=Team.get_all(get_db_conn()),
                           db=get_db_conn())


@app.route('/manage/teams/new', methods=['GET', 'POST'])
def manage_teams_new():
    if request.method == 'POST' and request.form['name'].strip():
        year = request.form['year'].strip()
        if not year:
            year = datetime.datetime.now().year
        Team.create(request.form['name'].strip(), year, get_db_conn())
        return redirect('/manage/teams')
    return render_template('manage/teams_new.html', categories=Category.fetch_all(get_db_conn()))


@app.route('/manage/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        print(type(request.form['newcategory']))
        get_db_conn().execute("INSERT INTO categories (name) VALUES (%s)", (request.form['newcategory'],), True)
    return render_template('manage/categories.html', categories=Category.fetch_all(get_db_conn()))


# TODO: CSRF or so...
@app.route('/manage/category/<category>', methods=['POST'])
def delete_category(category):
    if 'delete' in request.form:
        category = int(category)
        get_db_conn().execute("DELETE FROM categories WHERE id=(%s)", (category,), None)
    return redirect('/manage/categories')


# TODO: guess question
@app.route('/manage/questions/new', methods=['GET', 'POST'])
def manage_questions_new():
    if request.method == 'POST' and request.form['ansA'].strip() and request.form['ansB'].strip() and \
            request.form['ansC'].strip() and request.form['ansD'].strip():
        question = get_db_conn().execute("INSERT INTO questions (question, category) VALUES (%s, %s)",
                                         (request.form['question'], request.form['category']), True)
        correct = request.form['correct']
        ans_ids = list()
        ans_ids.append(get_db_conn().execute("INSERT INTO answers (answers, answer) VALUES (%s, %s)",
                                             (question, request.form['ansA'].strip()), True))
        ans_ids.append(get_db_conn().execute("INSERT INTO answers (answers, answer) VALUES (%s, %s)",
                                             (question, request.form['ansB'].strip()), True))
        ans_ids.append(get_db_conn().execute("INSERT INTO answers (answers, answer) VALUES (%s, %s)",
                                             (question, request.form['ansC'].strip()), True))
        ans_ids.append(get_db_conn().execute("INSERT INTO answers (answers, answer) VALUES (%s, %s)",
                                             (question, request.form['ansD'].strip()), True))

        get_db_conn().execute("UPDATE questions SET correct = %s WHERE id = %s",
                              (ans_ids[ord(correct) - 97], question), True)
        return redirect('/manage/questions/new')
    return render_template('manage/questions_new.html', categories=Category.fetch_all(get_db_conn()))


@app.route('/manage/question/<question>/edit', methods=['GET', 'POST'])
def edit_question(question):
    question = int(question)
    if request.method == 'POST':
        if 'delete' in request.form:
            get_db_conn().execute("DELETE questions WHERE id = %s", (question,), None)
            return redirect('/manage/questions')
        quest_obj = Question.get_by_id(question, get_db_conn())
        correct = request.form['correct']
        get_db_conn().execute("UPDATE questions SET question = %s, category = %s, correct = %s WHERE id = %s",
                              (request.form['question'], request.form['category'],
                               quest_obj.answers[ord(correct) - 97].id, question), True)
        get_db_conn().execute("UPDATE answers set answer = %s WHERE id=%s",
                              (request.form['ansA'].strip(), request.form['aid']), True)
        get_db_conn().execute("UPDATE answers set answer = %s WHERE id=%s",
                              (request.form['ansB'].strip(), request.form['bid']), True)
        get_db_conn().execute("UPDATE answers set answer = %s WHERE id=%s",
                              (request.form['ansC'].strip(), request.form['cid']), True)
        get_db_conn().execute("UPDATE answers set answer = %s WHERE id=%s",
                              (request.form['ansD'].strip(), request.form['did']), True)

        return redirect('/manage/question/{}/edit'.format(question))
    return render_template('manage/questions_new.html', q=Question.get_by_id(question, get_db_conn()),
                           categories=Category.fetch_all(get_db_conn()))


@app.route('/manage/run/<token>/<q>')
def run_display(token, q):
    res = get_db_conn().execute("SELECT * FROM device_api_tokens WHERE token=%s", (token,))
    if len(res) > 0:
        s = request.environ['beaker.session']
        s['device_token'] = DeviceToken(**res[0])
        s.save()
        active_displays[token].active_quiz = Quiz.get_by_id(q, get_db_conn())
        print(active_displays[token].active_quiz)
        active_displays[token].ready = False
        return redirect('/quiz_manager')


@app.route('/manage/displays')
def manage_displays():
    return render_template('/manage/displays.html', displays=active_displays)


@app.route('/manage/arrange/<quiz>', methods=['GET', 'POST'])
def manage_arrange_edit(quiz):
    if request.method == 'POST':
        get_db_conn().execute("UPDATE quizes SET name=%s, year=%s, public=%s WHERE id=%s",
                              (request.form['name'], request.form['year'], request.form['public'], quiz), True)
        return redirect('/manage/arrange')
    return render_template('manage/arrange_new.html', q=Quiz.get_by_id(quiz, get_db_conn()))


@app.route('/manage/arrange/<quiz>/add', methods=['GET'])
def manage_arrange_question(quiz):
    Quiz.get_by_id(quiz, db=get_db_conn()).add(Question.get_by_id(db=get_db_conn(), id=request.args.get('id')),
                                               db=get_db_conn())
    return redirect('/manage/questions')


@app.route('/manage/clients', methods=['GET', 'POST'])
def manage_arrange_device_tokens():
    if request.method == 'POST':
        get_db_conn().execute("INSERT INTO device_api_tokens (description, token) VALUES(%s, %s)",
                              (request.form['newtoken'], str(uuid.uuid4())), True)
        return redirect('/manage/clients')
    return render_template('/manage/device_tokens.html', devices=DeviceToken.get_all(get_db_conn()))


@app.route('/manage/client/<device>', methods=['POST'])
def manage_edit_device_token(device):
    if 'delete' in request.form:
        get_db_conn().execute("DELETE FROM device_api_tokens WHERE id=%s", (device,), None)
    return redirect('/manage/clients')


@app.route('/manage/arrange', methods=['GET', 'POST'])
def manage_arrange():
    if request.method == 'POST':
        get_db_conn().execute("DELETE FROM quizes WHERE id=%s", (request.form['id']), None)
        return redirect("/manage/arrange")
    return render_template('manage/arrange.html',
                           questions=[Quiz(**q) for q in get_db_conn().execute("SELECT * FROM quizes")],
                           displays=[d for d in active_displays.values() if d.ready])


@app.route('/manage/arrange/new', methods=['GET', 'POST'])
def manage_arrange_new():
    if request.method == 'POST':
        year = int(request.args.get('year', datetime.datetime.now().year))
        name = request.form['name']
        get_db_conn().execute("INSERT INTO quizes (name, year, public) VALUES(%s, %s, %s)",
                              (name, year, 'public' in request.form), True)
        return redirect("/manage/arrange")
    return render_template('manage/arrange_new.html')


# USER PAGES
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'device_token' in request.environ['beaker.session']:
        return render_template('try.html')
    return redirect('/display')


@app.route('/quiz_manager', methods=['GET', 'POST'])
def quiz_manage():
    if 'device_token' in request.environ['beaker.session']:
        return render_template('manage_display.html')
    return redirect('/display')


@app.route('/clear_session')
def clear_session():
    request.environ['beaker.session'].delete()
    return redirect('/')


@app.route('/display', methods=['GET', 'POST'])
def display():
    if request.method == 'POST':
        res = get_db_conn().execute("SELECT * FROM device_api_tokens WHERE token=%s", (request.form['token'],))
        if len(res) > 0:
            s = request.environ['beaker.session']
            s['device_token'] = DeviceToken(**res[0])
            s.save()
            return redirect('/quiz')
    return render_template('display_login.html')


# SOCKET.IO STUFF

def emit_question(question, dev):
    print("emit", question.question)
    emit('question', {'question': question.question, 'a': question.answers[0].answer,
                      'b': question.answers[1].answer, 'c': question.answers[2].answer,
                      'd': question.answers[3].answer}, room=dev.token)


@socketio.on('connect', namespace='/quiz')
def quiz_connect():
    # emit('question', {'question': 'Connected', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd'})
    s = request.environ['beaker.session']
    if 'device_token' in s:
        print("Device token detected!")
        join_room(s['device_token'].token)
        dev = s['device_token']
        emit('meta_data', {'display_name': dev.name}, room=dev.token)
        if dev.token in active_displays and not active_displays[dev.token].ready:
            disp = active_displays[dev.token]
            current_quest = disp.active_quiz.get_current_question(get_db_conn())
            emit_question(current_quest, dev)
        else:
            active_displays[dev.token] = Display(dev)
        print(s['device_token'].name, 'was added as active screen.')
    print("Connected")


@socketio.on('disconnect', namespace='/quiz')
def quiz_disconnect():
    s = request.environ['beaker.session']['device_token']
    leave_room(s.token)
    # del (active_displays[s.token])
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
    index = ord(ans) - 97
    correct_index = 0
    quest = disp.active_quiz.get_current_question(get_db_conn())
    for a in quest.answers:
        if a.id == quest.correct.id:
            break
        correct_index += 1
    emit('answer_response', {'correct': chr(97 + correct_index)}, room=disp.token.token)


@socketio.on('answer_selected', namespace='/quiz')
def answer_selected(message):
    disp = active_displays[request.environ['beaker.session']['device_token'].token]
    if not disp.w:
        return
    ans = message['sel']
    emit('selection', {'selected': ans}, room=disp.token.token)


@socketio.on('pause_quiz', namespace='/quiz')
def pause_quiz(message):
    disp = active_displays[request.environ['beaker.session']['device_token'].token]
    if not disp.w:
        return
    emit('sleep', {}, room=disp.token.token)


@socketio.on('resume_quiz', namespace='/quiz')
def resmue_quiz(message):
    disp = active_displays[request.environ['beaker.session']['device_token'].token]
    if not disp.w:
        return
    emit('wakeup', {}, room=disp.token.token)


@socketio.on('next_question', namespace='/quiz')
def next_q(message):
    dev = request.environ['beaker.session']['device_token']
    disp = active_displays[dev.token]
    emit_question(disp.active_quiz.get_next_question(get_db_conn()), dev)


@socketio.on('prev_question', namespace='/quiz')
def prev_q(message):
    dev = request.environ['beaker.session']['device_token']
    disp = active_displays[dev.token]
    emit_question(disp.active_quiz.get_prev_question(get_db_conn()), dev)


@socketio.on('cancel_quiz', namespace='/quiz')
def cancel_quiz(message):
    dev = request.environ['beaker.session']['device_token']
    disp = active_displays[dev.token]



if __name__ == '__main__':
    app.run(threaded=True)
