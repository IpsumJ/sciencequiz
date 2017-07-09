from flask import Flask, render_template, request, redirect, g
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
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

db = SQLAlchemy(app)
from model import *

db.create_all()

app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)


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
    q = Quiz.query.all()
    c = Category.query.all()
    return render_template('manage/questions.html', categories=c,
                           quizzes=q)


@app.route('/manage/teams')
def manage_teams():
    return render_template('manage/teams.html', teams=Team.query.all())


@app.route('/manage/teams/new', methods=['GET', 'POST'])
def manage_teams_new():
    if request.method == 'POST' and request.form['name'].strip():
        year = request.form['year'].strip()
        if not year:
            year = datetime.datetime.now().year
        t = Team(name=request.form['name'].strip(), year=year)
        db.session.add(t)
        db.session.commit()
        return redirect('/manage/teams')
    cat = Category.query.all()
    db.session.commit()
    return render_template('manage/teams_new.html', categories=cat)


@app.route('/manage/categories', methods=['GET', 'POST'])
def manage_categories():
    if request.method == 'POST':
        c = Category(name=request.form['newcategory'])
        db.session.add(c)
        db.session.commit()
    cat = Category.query.all()
    db.session.commit()
    return render_template('manage/categories.html', categories=cat)


# TODO: CSRF or so...
@app.route('/manage/category/<category>', methods=['POST'])
def delete_category(category):
    if 'delete' in request.form:
        Category.query.filter(Category.id == int(category)).delete()
        db.session.commit()
    return redirect('/manage/categories')


# TODO: guess question
@app.route('/manage/questions/new', methods=['GET', 'POST'])
def manage_questions_new():
    if request.method == 'POST' and request.form['ansA'].strip() and request.form['ansB'].strip() and \
            request.form['ansC'].strip() and request.form['ansD'].strip():
        print(request.form['category'])
        question = Question(question=request.form['question'], category=request.form['category'])
        correct = ord(request.form['correct'].upper())
        correct_answer = None
        # db.mapper(Question, db.metadata.tables['questions'], non_primary=True, properties={'correct_answer': db.relationship(Answer)})
        for i in range(ord('A'), ord('E')):
            a = Answer(question=question, answer=request.form['ans' + chr(i)])
            question.answers.append(a)
            if i == correct:
                correct_answer = a
        db.session.add(question)
        db.session.commit()
        print(correct_answer.id)
        question.correct_answer = correct_answer.id
        db.session.commit()
        return redirect('/manage/questions/new')

    categories = Category.query.all()
    db.session.commit()
    return render_template('manage/questions_new.html', categories=categories)


@app.route('/manage/question/<question>/edit', methods=['GET', 'POST'])
def edit_question(question):
    question = int(question)
    if request.method == 'POST':
        if 'delete' in request.form:
            Question.query.filter_by(id=question).delete()
            db.session.commit()
            return redirect('/manage/questions')
        quest_obj = Question.query.get(question)
        correct = request.form['correct']
        quest_obj.question = request.form['question']
        quest_obj.category = request.form['category'],
        quest_obj.correct_answer = quest_obj.answers[ord(correct) - 97].id

        Answer.query.get(request.form['aid']).answer = request.form['ansA'].strip()
        Answer.query.get(request.form['bid']).answer = request.form['ansB'].strip()
        Answer.query.get(request.form['cid']).answer = request.form['ansC'].strip()
        Answer.query.get(request.form['did']).answer = request.form['ansD'].strip()
        db.session.commit()
        return redirect('/manage/question/{}/edit'.format(question))
    q = Question.query.get(question)
    cat = Category.query.all()
    db.session.commit()
    return render_template('manage/questions_new.html', q=q,
                           categories=cat)


@app.route('/manage/run/<token>/<q>')
def run_display(token, q):
    res = DeviceToken.query.filter_by(token=token)
    if res is not None:
        s = request.environ['beaker.session']
        s['device_token'] = res[0]
        s.save()
        active_displays[token].active_quiz = Quiz.query.get(q)
        active_displays[token].quiz_index = 0
        print(active_displays[token].active_quiz)
        active_displays[token].ready = False
        return redirect('/quiz_manager')
    db.session.commit()


@app.route('/manage/displays')
def manage_displays():
    return render_template('/manage/displays.html', displays=active_displays)


@app.route('/manage/arrange/<quiz>', methods=['GET', 'POST'])
def manage_arrange_edit(quiz):
    if request.method == 'POST':
        q = Quiz.query.get(quiz)
        q.name = request.form['name']
        q.year = request.form['year']
        q.public = 'public' in request.form
        db.session.commit()
        return redirect('/manage/arrange')
    q = Quiz.query.get(quiz)
    db.session.commit()
    return render_template('manage/arrange_new.html', q=q)


@app.route('/manage/arrange/<quiz>/add', methods=['GET'])
def manage_arrange_question(quiz):
    q = Question.query.get(request.args.get('id'))
    q.quizzes.append(Quiz.query.get(quiz))
    db.session.commit()
    return redirect('/manage/questions')


@app.route('/manage/clients', methods=['GET', 'POST'])
def manage_arrange_device_tokens():
    if request.method == 'POST':
        db.session.add(DeviceToken(name=request.form['newtoken'], token=str(uuid.uuid4())))
        db.session.commit()
        return redirect('/manage/clients')
    devs = DeviceToken.query.all()
    return render_template('/manage/device_tokens.html', devices=devs)


@app.route('/manage/client/<device>', methods=['POST'])
def manage_edit_device_token(device):
    if 'delete' in request.form:
        DeviceToken.query.filter_by(id=device).delete()
        db.session.commit()
    return redirect('/manage/clients')


@app.route('/manage/arrange', methods=['GET', 'POST'])
def manage_arrange():
    if request.method == 'POST':
        Quiz.query.filter_by(id=request.form['id']).delete()
        db.session.commit()
        return redirect("/manage/arrange")
    q = Quiz.query.all()
    db.session.commit()
    return render_template('manage/arrange.html',
                           quizzes=q,
                           displays=[d for d in active_displays.values() if d.ready])


@app.route('/manage/arrange/new', methods=['GET', 'POST'])
def manage_arrange_new():
    if request.method == 'POST':
        year = int(request.args.get('year', datetime.datetime.now().year))
        name = request.form['name']
        q = Quiz(name=name, year=year, public='public' in request.form)
        db.session.add(q)
        db.session.commit()
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
        res = DeviceToken.query.filter_by(token=request.form['token'])
        db.session.commit()
        if res is not None:
            s = request.environ['beaker.session']
            s['device_token'] = res[0]
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
            current_quest = disp.active_quiz.questions[disp.quiz_index]
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
    quest = disp.active_quiz.questions[disp.quiz_index]
    for a in quest.answers:
        if a.id == quest.correct_answer:
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
    disp.quiz_index += 1
    emit_question(disp.active_quiz.questions[disp.quiz_index], dev)


@socketio.on('prev_question', namespace='/quiz')
def prev_q(message):
    dev = request.environ['beaker.session']['device_token']
    disp = active_displays[dev.token]
    disp.quiz_index -= 1
    emit_question(disp.active_quiz.questions[disp.quiz_index], dev)


@socketio.on('cancel_quiz', namespace='/quiz')
def cancel_quiz(message):
    dev = request.environ['beaker.session']['device_token']
    disp = active_displays[dev.token]


if __name__ == '__main__':
    app.run(port=app.config.get('PORT'), threaded=True)
