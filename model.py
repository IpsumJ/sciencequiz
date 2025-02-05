from sciencequiz import db
import enum
import datetime

association_quiz_questions = db.Table('quiz_questions', db.Model.metadata,
                                      db.Column('quiz_id', db.Integer, db.ForeignKey('quizzes.id')),
                                      db.Column('question_id', db.Integer, db.ForeignKey('questions.id'))
                                      )


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    questions = db.relationship("Question", order_by="Question.id")


class QuestionType(enum.Enum):
    choose = 1
    estimate = 2


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.ForeignKey('categories.id'), nullable=False)
    image_file_name = db.Column(db.String(200), nullable=True)  # Optionales Bilds zur Frage
    quizzes = db.relationship('Quiz', secondary=association_quiz_questions,
                              back_populates='questions')
    type = db.Column(db.Enum(QuestionType))
    __mapper_args__ = {
        'polymorphic_on': type
    }


class QuestionChoose(Question):
    correct_answer_id = db.Column(db.ForeignKey('answers_choose.id'),
                               nullable=True)  # Has to be nullable because of inheritance. Use join instead?
    answers = db.relationship('AnswerChoose', foreign_keys='[AnswerChoose.question_id]', order_by="AnswerChoose.id")
    __mapper_args__ = {
        'polymorphic_identity': QuestionType.choose
    }


class QuestionEstimate(Question):
    correct_value = db.Column(db.Float, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': QuestionType.estimate
    }


class AnswerChoose(db.Model):
    __tablename__ = 'answers_choose'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.ForeignKey('questions.id', ondelete='CASCADE'),
                         nullable=False)  # Can we specify this is only valid for QuestionChoose?
    question = db.relationship("QuestionChoose", foreign_keys="[AnswerChoose.question_id]")
    answer = db.Column(db.String(250), nullable=False)


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    public = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    questions = db.relationship("Question", secondary=association_quiz_questions,
                                back_populates="quizzes", order_by="Question.id")


class DeviceToken(db.Model):
    __tablename__ = 'device_tokens'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    token = db.Column(db.String(250), nullable=False, unique=True)


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    team_sessions = db.relationship('TeamSession')
    members = db.relationship('User')


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    team_id = db.Column(db.ForeignKey('teams.id'), nullable=True)

    # @staticmethod
    # def login(username, password, db):
    #    m = hashlib.sha512()
    #    m.update(password.encode('utf-8'))
    #    res = db.execute("SELECT id, username, admin, display_name FROM users WHERE username=%s AND password=%s",
    #                     (username, m.hexdigest()))
    #    if len(res) == 0:
    #        return None
    #    return User(**res[0])


class SessionState(enum.Enum):
    pending = 1
    running = 2
    paused = 3
    finished = 4
    closed = 5

class FinalTimerState(enum.Enum):
    waiting = 1
    running = 2
    finished = 3


class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.ForeignKey('quizzes.id'), nullable=False)
    quiz = db.relationship("Quiz")
    team_sessions = db.relationship('TeamSession')
    device_token_id = db.Column(db.ForeignKey('device_tokens.id'))
    device_token = db.relationship("DeviceToken")
    state = db.Column(db.Enum(SessionState), nullable=False)
    current_question_id = db.Column(db.ForeignKey('questions.id'), nullable=True)
    current_question = db.relationship('Question')
    start_time = db.Column(db.DateTime, nullable=True)  # Quiz is temporarily paused if start_time is NULL
    offset = db.Column(db.Interval, nullable=False, default=datetime.timedelta())
    timer_state = db.Column(db.Enum(FinalTimerState), nullable=False);

    @classmethod
    def on_display(cls):
        '''
        Whether the session should currently be displayed in its room
        '''
        return db.or_(cls.state == SessionState.running, cls.state == SessionState.finished, cls.state == SessionState.paused)
    def isfinal(self):
        return len(self.team_sessions) == 4


class TeamSession(db.Model):
    __tablename__ = 'team_sessions'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.ForeignKey('teams.id'), nullable=False)
    team = db.relationship("Team")
    session_id = db.Column(db.ForeignKey('sessions.id'), nullable=False)
    session = db.relationship("Session")
    answers = db.relationship("TeamAnswer")

    def score(self):
        result = 0.0
        for answer in self.answers:
            if isinstance(answer, TeamAnswerChoose):
                answer_choose = answer.answer
                if answer_choose.question.correct_answer_id == answer_choose.id:
                    if answer.answer_type == AnswerType.normal:
                        result += 1.0
                    elif answer.answer_type == AnswerType.final_first:
                        result += 2.0
            elif isinstance(answer, TeamAnswerEstimate):
                correct_estimate = answer.question.correct_value
                other_estimates = TeamAnswerEstimate.query.join(TeamAnswerEstimate.team_session).filter(
                                      TeamSession.session_id == self.session_id,  # Same session
                                      TeamAnswerEstimate.question_id == answer.question_id,  # Same question
                                      TeamAnswerEstimate.id != answer.id  # Not me
                                  ).options(db.load_only("estimate")).all()
                other_estimate_dists = [abs(x.estimate - correct_estimate) for x in other_estimates]
                my_estimate_dist = abs(answer.estimate - correct_estimate)
                # TODO implement answer type
                if len(other_estimate_dists) == 0:
                    result += 1.0
                else:
                    best_other_dist = min(other_estimate_dists)
                    if my_estimate_dist < best_other_dist:
                        result += 1.0
            else:
                print("WAT?")
        return result

class AnswerType(enum.Enum):
    normal = 1
    final_first = 2

class TeamAnswer(db.Model):
    __tablename__ = 'team_answers'
    id = db.Column(db.Integer, primary_key=True)
    team_session_id = db.Column(db.ForeignKey('team_sessions.id'), nullable=False)
    team_session = db.relationship("TeamSession")
    answer_type = db.Column(db.Enum(AnswerType), nullable=False);
    type = db.Column(db.Enum(QuestionType))
    __mapper_args__ = {
        'polymorphic_on': type
    }


class TeamAnswerChoose(TeamAnswer):
    answer_id = db.Column(db.ForeignKey('answers_choose.id'), nullable=True)
    answer = db.relationship("AnswerChoose")
    __mapper_args__ = {
        'polymorphic_identity': QuestionType.choose
    }


class TeamAnswerEstimate(TeamAnswer):
    question_id = db.Column(db.ForeignKey('questions.id'), nullable=True)
    question = db.relationship("Question")
    estimate = db.Column(db.Float, nullable=True)
    __mapper_args__ = {
        'polymorphic_identity': QuestionType.estimate
    }


class Display(object):
    def __init__(self, token, r=True, w=False):
        self.r = r
        self.w = w
        self.token = token
