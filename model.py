from sciencequiz import db

association_quiz_questions = db.Table('quiz_questions', db.Model.metadata,
                                      db.Column('quiz', db.Integer, db.ForeignKey('quizzes.id')),
                                      db.Column('question', db.Integer, db.ForeignKey('questions.id'))
                                      )


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    questions = db.relationship("Question")


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    category = db.Column(db.ForeignKey('categories.id'), nullable=False)
    correct_answer = db.Column(db.ForeignKey('answers.id'), nullable=True)  # arrrrgh!
    answers = db.relationship('Answer', foreign_keys='[Answer.question]', backref='Answer.question',
                              cascade='all,delete')
    quizzes = db.relationship('Quiz', secondary=association_quiz_questions,
                              back_populates='questions')


class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    answer = db.Column(db.String(250), nullable=False)


class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    public = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String(250), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    questions = db.relationship("Question", secondary=association_quiz_questions,
                                back_populates="quizzes")


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


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    display_name = db.Column(db.String(150), nullable=False)
    password = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(250), nullable=False)

    # @staticmethod
    # def login(username, password, db):
    #    m = hashlib.sha512()
    #    m.update(password.encode('utf-8'))
    #    res = db.execute("SELECT id, username, admin, display_name FROM users WHERE username=%s AND password=%s",
    #                     (username, m.hexdigest()))
    #    if len(res) == 0:
    #        return None
    #    return User(**res[0])


class Display(object):
    def __init__(self, token):
        self.token = token
        self.ready = True
        self.r = True
        self.w = True
        self.current_quiz = None
        self.quiz_index = 0
