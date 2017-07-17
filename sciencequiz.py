from flask import Flask, render_template, request, redirect, abort, send_from_directory, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from beaker.middleware import SessionMiddleware
import uuid
import time
import os
import traceback

# TODO!!!: Error handling

session_opts = {
    'session.type': 'file',
    'session.url': '127.0.0.1:5000',
    'session.data_dir': './cache',
}

app = Flask(__name__)
socketio = SocketIO(app)
app.config.from_pyfile('config.py')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'svg'])

timer_thread = None

db = SQLAlchemy(app)
from model import *

db.create_all()

app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
def inject_upload_folder():
    return dict(upload_folder=app.config.get('UPLOAD_FOLDER'))


@app.context_processor
def inject_questiontypes():
    return dict(isinstance=isinstance, QuestionChoose=QuestionChoose,
                QuestionEstimate=QuestionEstimate, QuestionType=QuestionType)


@app.route('/')
def science_quiz():
    # return render_template('main.html', title="ScienceQuiz")
    return redirect(url_for('manage'))


# MANAGE PAGES
@app.route('/media/<file>')
def serve_image(file):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               file)


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
            if session.state != SessionState.running and session.state != SessionState.paused:
                abort(400, "Session not running.")
            session.current_question = None
            session.state = SessionState.pending
            db.session.commit()
            emit_state(session.device_token)
        if action == 'run':
            if session.state == SessionState.finished:
                abort(400, "Session already finished.")
            if Session.query.filter(Session.on_display(),
                                    Session.device_token_id == session.device_token_id).count() > 0:
                abort(400, "A session is already running in this room.")
            session.state = SessionState.paused
            db.session.commit()
            emit_state(session.device_token)
        if action == 'close':
            if session.state == SessionState.closed:
                abort(400, "Session already closed.")
            if session.state == SessionState.pending:
                abort(400, "Session not running or finished.")
            session.state = SessionState.closed
            db.session.commit()
            emit_state(session.device_token)
        redirect('/manage/sessions')
    return render_template('manage/sessions.html', sessions=Session.query.all())


@app.route('/manage/sessions/new', methods=['GET', 'POST'])
def manage_sessions_new():
    if request.method == 'POST':
        s = Session(quiz_id=request.form['quiz'], state=SessionState.pending,
                    device_token_id=request.form['device_token'])
        db.session.add(s)
        num_teams = 0
        for i in range(4):
            team_id = request.form['team' + str(i)]
            if team_id:
                num_teams += 1
                ts = TeamSession(session=s, team_id=team_id)
                db.session.add(ts)
        if num_teams == 0:
            db.session.rollback()
            abort(400, "Session must have at least one team")
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


def handle_question_image():
    if 'question_image' in request.files:
        file = request.files['question_image']
        if file.filename is not '':
            if file and allowed_file(file.filename):
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return filename
    return None


# TODO: guess question
@app.route('/manage/questions/new', methods=['GET', 'POST'])
def manage_questions_new():
    question = None
    if request.method == 'POST':
        if QuestionType[request.form['type']] == QuestionType.choose:
            if not (request.form['ansA'].strip() and request.form['ansB'].strip() and
                        request.form['ansC'].strip() and request.form['ansD'].strip()):
                abort(400, "Some anwers are empty")
            question = QuestionChoose(question=request.form['question'], category_id=request.form['category'])
            correct = ord(request.form['correct'].upper())
            correct_answer = None
            # db.mapper(Question, db.metadata.tables['questions'], non_primary=True, properties={'correct_answer': db.relationship(Answer)})
            for i in range(ord('A'), ord('E')):
                a = AnswerChoose(question_id=question, answer=request.form['ans' + chr(i)])
                question.answers.append(a)
                if i == correct:
                    correct_answer = a
            question.image_file_name = handle_question_image()
            db.session.add(question)
            db.session.commit()
            question.correct_answer_id = correct_answer.id
            db.session.commit()
        elif QuestionType[request.form['type']] == QuestionType.estimate:
            question = QuestionEstimate(question=request.form['question'],
                                        category_id=request.form['category'],
                                        correct_value=float(request.form['correct_value']))
            question.image_file_name = handle_question_image()
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
            quest = Question.query.filter_by(id=question)
            q_obj = quest.first()
            if q_obj.image_file_name is not None:
                os.unlink(os.path.join(app.config.get('UPLOAD_FOLDER'), q_obj.image_file_name))
            quest.delete()
            db.session.commit()
            return redirect('/manage/questions')
        quest_obj = Question.query.get(question)
        if isinstance(quest_obj, QuestionChoose):
            correct = request.form['correct']
            quest_obj.question = request.form['question']
            quest_obj.category = request.form['category'],
            quest_obj.correct_answer_id = quest_obj.answers[ord(correct) - 97].id

            AnswerChoose.query.get(request.form['aid']).answer = request.form['ansA'].strip()
            AnswerChoose.query.get(request.form['bid']).answer = request.form['ansB'].strip()
            AnswerChoose.query.get(request.form['cid']).answer = request.form['ansC'].strip()
            AnswerChoose.query.get(request.form['did']).answer = request.form['ansD'].strip()
            image = handle_question_image()
            if quest_obj.image_file_name is not None and image is None:
                os.unlink(os.path.join(app.config.get('UPLOAD_FOLDER'), quest_obj.image_file_name))
            if image is not None:
                quest_obj.image_file_name = image
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
    return render_template('/manage/active_sessions.html', sessions=Session.query.filter(Session.on_display()))


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
def manage_arrange_question_add(quiz):
    q = Question.query.get(request.args.get('id'))
    q.quizzes.append(Quiz.query.get(quiz))
    db.session.commit()
    return redirect('/manage/questions')


@app.route('/manage/arrange/<quiz>/delete', methods=['POST'])
def manage_arrange_question_delete(quiz):
    q = Question.query.get(request.form['id'])
    q.quizzes.remove(Quiz.query.get(quiz))
    db.session.commit()
    return redirect('/manage/arrange/{}'.format(quiz))


@app.route('/manage/rooms', methods=['GET', 'POST'])
def manage_arrange_device_tokens():
    if request.method == 'POST':
        if not request.form['newtoken']:
            abort(400, "Name must not be empty")
        db.session.add(DeviceToken(name=request.form['newtoken'], token=str(uuid.uuid4())))
        db.session.commit()
        return redirect('/manage/rooms')
    devs = DeviceToken.query.all()
    return render_template('/manage/device_tokens.html', devices=devs)


@app.route('/manage/room/<device>', methods=['POST'])
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

def timer_task():
    while True:
        sessions = Session.query.options(db.joinedload(Session.device_token)).filter(
            Session.state == SessionState.running).all()
        for session in sessions:
            try:
                if session.device_token is not None:
                    time_running = None
                    if session.start_time is None:
                        time_running = session.offset
                    else:
                        time_running = datetime.datetime.now() - session.start_time + session.offset
                    time_total = datetime.timedelta(minutes=15)
                    socketio.emit('timer', {'time_running': time_running.total_seconds(),
                                            'time_total': time_total.total_seconds()}, room=session.device_token.token,
                                  namespace="/quiz")
                    if time_running > time_total:
                        finish_session(session)
                        db.session.commit()
                        emit_state(session.device_token)
            except Exception as e:
                print("Exception occurred in timer, please dont die...")
                print(e)
        db.session.rollback()  # Needed to include newer commits in result

        time.sleep(0.5)


def finish_session(session):
    pause_timer(session)
    session.state = SessionState.finished


def pause_timer(session):
    if session.start_time is not None:
        session.offset += datetime.datetime.now() - session.start_time
        session.start_time = None


def resume_timer(session):
    if session.start_time is None:
        session.start_time = datetime.datetime.now()


def emit_state(token):
    session = get_current_session_by_token(token)
    if session is None:
        socketio.emit('meta_data', {'display_name': token.name, 'team_names': []}, room=token.token, namespace="/quiz")
        socketio.emit('sleep', {}, room=token.token, namespace="/quiz")
        return

    socketio.emit('meta_data', {'display_name': token.name, 'team_names': [t.team.name for t in session.team_sessions]},
                  namespace="/quiz")

    if session.state == SessionState.finished:
        socketio.emit('wakeup', {}, room=token.token, namespace="/quiz")
        socketio.emit('finished', {'a': 'b', 'score': [t.score() for t in session.team_sessions]},
                      room=session.device_token.token, namespace="/quiz")
        return
    elif session.state == SessionState.paused:
        socketio.emit('sleep', {}, room=token.token, namespace="/quiz")
    elif session.state == SessionState.running:
        socketio.emit('wakeup', {}, room=token.token, namespace="/quiz")
    else:
        print("This should not happen")


def emit_question(question, dev):
    print("emit", question.question)
    token = DeviceToken.query.filter_by(token=dev.token).first()
    session = get_current_session_by_token(token)
    answers = TeamAnswerChoose.query.join(TeamAnswerChoose.team_session).filter(
        TeamSession.session_id == session.id).join(
        TeamAnswerChoose.answer).filter(AnswerChoose.question_id == question.id).all()
    print(type(answers))
    socketio.emit('question', {'question': {'id': question.id, 'question': question.question,
                                            'answers': [{'id': a.id, 'answer': a.answer} for a in question.answers],
                                            'image': question.image_file_name,
                                            'team_answers': [{str(a.team_session.team_id): a.answer_id} for a in
                                                             answers]}},
                  room=dev.token, namespace='/quiz')


def get_current_session_by_token(token):
    res = Session.query.filter(Session.on_display(), Session.device_token_id == token.id)
    if res.count() == 0:
        return None
    return res.first()


@socketio.on('connect', namespace='/quiz')
def quiz_connect():
    global timer_thread
    if timer_thread is None:
        timer_thread = socketio.start_background_task(target=timer_task)
    # emit('question', {'question': 'Connected', 'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd'})
    s = request.environ['beaker.session']
    if 'display' in s:
        disp = s['display']
        token = DeviceToken.query.filter_by(token=disp.token).first()
        join_room(token.token)
        session = get_current_session_by_token(token)
        emit('meta_data', {'display_name': token.name, 'teams': []}, room=token.token)
        if session is None:
            emit('sleep', room=token.token)
        else:
            if session.current_question is not None:
                print('emit current')
                emit_question(session.current_question, disp)
            emit('meta_data',
                 {'display_name': token.name,
                  'teams': [{'id': t.team.id, 'name': t.team.name} for t in session.team_sessions]})
            emit_state(token)


@socketio.on('disconnect', namespace='/quiz')
def quiz_disconnect():
    s = request.environ['beaker.session']['display']
    leave_room(room=s.token)
    print('disconnect', s.token)


# TODO!
@socketio.on('answer_selected_result', namespace='/quiz')
def answer_selected_result(message):
    disp = request.environ['beaker.session']['display']
    if not disp.w:
        return
    token = DeviceToken.query.filter_by(token=disp.token).first()
    quest = get_current_session_by_token(token).current_question
    if isinstance(quest, QuestionChoose):
        emit('answer_response', {'correct': quest.correct_answer_id}, room=disp.token)


# TODO!
@socketio.on('answer_selected', namespace='/quiz')
def answer_selected(message):
    disp = request.environ['beaker.session']['display']
    if not disp.w:
        return
    ans = message['id']
    token = DeviceToken.query.filter_by(token=disp.token).first()
    session = get_current_session_by_token(token=token)
    pause_timer(session)
    db.session.commit()
    choose = None
    if isinstance(session.current_question, QuestionChoose):
        # TODO! multiteam
        choose = TeamAnswerChoose(team_session=session.team_sessions[0],
                                  answer_id=ans)
    elif isinstance(session.current_question, QuestionEstimate):
        # TODO
        pass
    db.session.add(choose)
    db.session.commit()
    emit('selection', {'selected': ans}, room=disp.token)


@socketio.on('pause_quiz', namespace='/quiz')
def pause_quiz(message):
    disp = request.environ['beaker.session']['display']
    if not disp.w:
        return
    token = DeviceToken.query.filter_by(token=disp.token).first()
    session = get_current_session_by_token(token)
    pause_timer(session)
    session.state = SessionState.paused
    db.session.commit()
    emit('sleep', {}, room=disp.token)


@socketio.on('resume_quiz', namespace='/quiz')
def resmue_quiz(message):
    disp = request.environ['beaker.session']['display']
    if not disp.w:
        return
    token = DeviceToken.query.filter_by(token=disp.token).first()
    session = get_current_session_by_token(token)
    resume_timer(session)
    session.state = SessionState.running
    db.session.commit()
    emit('wakeup', {}, room=disp.token)


@socketio.on('next_question', namespace='/quiz')
def next_q(message):
    disp = request.environ['beaker.session']['display']
    token = DeviceToken.query.filter_by(token=disp.token).first()
    session = get_current_session_by_token(token)
    resume_timer(session)
    db.session.commit()
    quiz = session.quiz
    qs = quiz.questions
    current = None
    # $mal zeit reinstecken, dass in einer query zu machen und nicht.... so:
    if session.current_question is None:
        current = qs[0]
    else:
        eq = False
        for q in qs:
            if eq:
                current = q
                break
            if q.id == session.current_question.id:
                eq = True
        if current is None:
            print('TODO quiz is finished')
            return
    session.current_question = current
    db.session.commit()
    emit_question(current, disp)


# TODO!
@socketio.on('prev_question', namespace='/quiz')
def prev_q(message):
    disp = request.environ['beaker.session']['display']
    token = DeviceToken.query.filter_by(token=disp.token).first()
    session = get_current_session_by_token(token)
    resume_timer(session)
    db.session.commit()
    quiz = session.quiz
    qs = quiz.questions
    current = None
    # $mal zeit reinstecken, dass in einer query zu machen und nicht.... so:
    if session.current_question is None:
        current = qs[0]
    else:
        eq = False
        prev = None
        for q in qs:
            if q.id == q.id == session.current_question.id:
                eq = True
            if eq:
                current = prev
                break
            prev = q
        if current is None:
            current = qs[0]
    session.current_question = current
    db.session.commit()
    emit_question(current, disp)


@socketio.on('finish_quiz', namespace='/quiz')
def finish_quiz(message):
    print("Finish quiz")
    disp = request.environ['beaker.session']['display']
    token = DeviceToken.query.filter_by(token=disp.token).first()
    session = get_current_session_by_token(token)
    finish_session(session)
    db.session.commit()
    emit_state(session.device_token)


@socketio.on('cancel_quiz', namespace='/quiz')
def cancel_quiz(message):
    disp = request.environ['beaker.session']['display']
    print('Sleep quiz')
    emit('sleep', {}, room=disp.token)


@app.errorhandler(Exception)
def err_rollback(err):
    print("Rollback.")
    traceback.print_exc()
    db.session.rollback()
    return 'An error occured.', 500


if __name__ == '__main__':
    app.run(port=app.config.get('PORT'), threaded=True)
