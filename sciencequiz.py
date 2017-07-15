from flask import Flask, render_template, request, redirect, abort
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from beaker.middleware import SessionMiddleware
import datetime
import uuid

# TODO!!!: Error handling

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

@app.context_processor
def inject_questiontypes():
    return dict(isinstance=isinstance, QuestionChoose=QuestionChoose,
            QuestionEstimate=QuestionEstimate, QuestionType=QuestionType)


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


@app.route('/manage/sessions', methods=['GET', 'POST'])
def manage_sessions():
    if 'action' in request.form:
        action = request.form['action']
        session = Session.query.get(request.form['session'])
        if action == 'cancel':
            if session.state == SessionState.finished:
                abort(400, "Session already finished.")
            session.state = SessionState.pending
            emit('meta_data', {'display_name': session.device_token.name, 'team_names': []},
                 room=session.device_token.token, namespace='/quiz')
            emit('sleep', {},
                 room=session.device_token.token, namespace='/quiz')
            db.session.commit()
        if action == 'run':
            if session.state == SessionState.finished:
                abort(400, "Session already finished.")
            if Session.query.filter_by(state=SessionState.running, device_token_id=session.device_token_id).count() > 0:
                abort(400, "A session is already running in this room.")
            session.state = SessionState.running
            emit('meta_data', {'display_name': session.device_token.name,
                               'team_names': [t.team.name for t in session.team_sessions]},
                 room=session.device_token.token, namespace='/quiz')
            db.session.commit()
        redirect('/manage/sessions')
    return render_template('manage/sessions.html', sessions=Session.query.all())


@app.route('/manage/sessions/new', methods=['GET', 'POST'])
def manage_sessions_new():
    if request.method == 'POST':
        s = Session(quiz_id=request.form['quiz'], state=SessionState.pending,
                    device_token_id=request.form['device_token'])
        db.session.add(s)
        for i in range(4):
            team_id = request.form['team' + str(i)]
            if team_id:
                ts = TeamSession(session=s, team_id=team_id)
                db.session.add(ts)
        db.session.commit()
        return redirect('/manage/sessions')
    return render_template('manage/sessions_new.html', quizzes=Quiz.query.all(), teams=Team.query.all(),
                           device_tokens=DeviceToken.query.all())


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
    if request.method == 'POST':
        if QuestionType[request.form['type']] == QuestionType.choose:
            if not(request.form['ansA'].strip() and request.form['ansB'].strip() and
                    request.form['ansC'].strip() and request.form['ansD'].strip()):
                abort(400, "Some anwers are empty")
            question = QuestionChoose(question=request.form['question'], category=request.form['category'])
            correct = ord(request.form['correct'].upper())
            correct_answer = None
            # db.mapper(Question, db.metadata.tables['questions'], non_primary=True, properties={'correct_answer': db.relationship(Answer)})
            for i in range(ord('A'), ord('E')):
                a = AnswerChoose(question=question, answer=request.form['ans' + chr(i)])
                question.answers.append(a)
                if i == correct:
                    correct_answer = a
            db.session.add(question)
            db.session.commit()
            question.correct_answer = correct_answer.id
            db.session.commit()
        elif QuestionType[request.form['type']] == QuestionType.estimate:
            question = QuestionEstimate(question=request.form['question'],
                    category=request.form['category'],
                    correct_value=float(request.form['correct_value']))
            db.session.add(question)
            db.session.commit()
        else:
            abort(400, "Unknown question type")
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
        if isinstance(quest_obj, QuestionChoose):
            correct = request.form['correct']
            quest_obj.question = request.form['question']
            quest_obj.category = request.form['category'],
            quest_obj.correct_answer = quest_obj.answers[ord(correct) - 97].id

            AnswerChoose.query.get(request.form['aid']).answer = request.form['ansA'].strip()
            AnswerChoose.query.get(request.form['bid']).answer = request.form['ansB'].strip()
            AnswerChoose.query.get(request.form['cid']).answer = request.form['ansC'].strip()
            AnswerChoose.query.get(request.form['did']).answer = request.form['ansD'].strip()
            db.session.commit()
        elif isinstance(quest_obj, QuestionEstimate):
            quest_obj.question = request.form['question']
            quest_obj.category = request.form['category'],
            quest_obj.correct_value = float(request.form['correct_value'])
            db.session.commit()
        else:
            abort(400, "Unknown question type")
        return redirect('/manage/questions')
    q = Question.query.get(question)
    cat = Category.query.all()
    db.session.commit()
    return render_template('manage/questions_new.html', q=q,
                           categories=cat)


@app.route('/run/<token>')
def run_r_display(token):
    res = DeviceToken.query.filter_by(token=token)
    if res.count() > 0:
        s = request.environ['beaker.session']
        s['display'] = Display(token=token)
        s.save()
        return redirect('/quiz')
    else:
        abort(403)


@app.route('/run_adm/<token>')
def run_rw_display(token):
    res = DeviceToken.query.filter_by(token=token)
    if res.count() > 0:
        s = request.environ['beaker.session']
        s['display'] = Display(w=True, token=token)
        s.save()
        return redirect('/quiz')
    else:
        abort(403)


@app.route('/manage/active_sessions')
def manage_displays():
    return render_template('/manage/active_sessions.html', sessions=Session.query.filter_by(state=SessionState.running))


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


@app.route('/manage/rooms', methods=['GET', 'POST'])
def manage_arrange_device_tokens():
    if request.method == 'POST':
        db.session.add(DeviceToken(name=request.form['newtoken'], token=str(uuid.uuid4())))
        db.session.commit()
        return redirect('/manage/rooms')
    devs = DeviceToken.query.all()
    return render_template('/manage/device_tokens.html', devices=devs)


@app.route('/manage/rooms/<device>', methods=['POST'])
def manage_edit_device_token(device):
    if 'delete' in request.form:
        DeviceToken.query.filter_by(id=device).delete()
        db.session.commit()
    return redirect('/manage/rooms')


@app.route('/manage/arrange', methods=['GET', 'POST'])
def manage_arrange():
    if request.method == 'POST':
        Quiz.query.filter_by(id=request.form['id']).delete()
        db.session.commit()
        return redirect("/manage/arrange")
    q = Quiz.query.all()
    db.session.commit()
    return render_template('manage/arrange.html',
                           quizzes=q)


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
    if 'display' in request.environ['beaker.session']:
        if request.environ['beaker.session']['display'].w:
            return render_template('manage_display.html')
        if request.environ['beaker.session']['display'].r:
            return render_template('display.html')
    abort(403)


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


def get_current_session_by_token(token):
    res = Session.query.filter_by(state=SessionState.running, device_token_id=token.id)
    if res.count() == 0:
        return None
    return res.first()


@socketio.on('connect', namespace='/quiz')
def quiz_connect():
    # emit('question', {'question': 'Connected', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd'})
    s = request.environ['beaker.session']
    if 'display' in s:
        display = s['display']
        token = DeviceToken.query.filter_by(token=display.token).first()
        join_room(token.token)
        session = get_current_session_by_token(token)
        emit('meta_data', {'display_name': token.name, 'team_names': []}, room=token.token)
        if session is None:
            emit('sleep', room=token.token)
        else:
            emit('meta_data', {'display_name': token.name, 'team_names': [t.team.name for t in session.team_sessions]})


@socketio.on('disconnect', namespace='/quiz')
def quiz_disconnect():
    s = request.environ['beaker.session']['display']
    print('disconnect', s.token)


# TODO!
@socketio.on('answer_selected_result', namespace='/quiz')
def answer_selected(message):
    disp = request.environ['beaker.session']['display']
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


# TODO!
@socketio.on('answer_selected', namespace='/quiz')
def answer_selected(message):
    disp = request.environ['beaker.session']['display']
    if not disp.w:
        return
    ans = message['sel']
    emit('selection', {'selected': ans}, room=disp.token.token)


@socketio.on('pause_quiz', namespace='/quiz')
def pause_quiz(message):
    disp = request.environ['beaker.session']['display']
    if not disp.w:
        return
    emit('sleep', {}, room=disp.token.token)


@socketio.on('resume_quiz', namespace='/quiz')
def resmue_quiz(message):
    disp = request.environ['beaker.session']['display']
    if not disp.w:
        return
    emit('wakeup', {}, room=disp.token.token)


@socketio.on('next_question', namespace='/quiz')
def next_q(message):
    disp = request.environ['beaker.session']['display']
    # disp.quiz_index += 1
    emit_question(disp.active_quiz.questions[disp.quiz_index], disp)


# TODO!
@socketio.on('prev_question', namespace='/quiz')
def prev_q(message):
    disp = request.environ['beaker.session']['display']
    # disp.quiz_index -= 1
    emit_question(disp.active_quiz.questions[disp.quiz_index], disp)


@socketio.on('cancel_quiz', namespace='/quiz')
def cancel_quiz(message):
    disp = request.environ['beaker.session']['display']
    print('Sleep quiz')
    emit('sleep', {}, room=disp.token)


if __name__ == '__main__':
    app.run(port=app.config.get('PORT'), threaded=True)
