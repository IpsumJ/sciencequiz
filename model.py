import hashlib


class Question(object):
    def __init__(self, id, question, category, image, db):
        self.id = id
        self.question = question
        self.category = Category.get_by_id(category, db)
        self.answers = [Answer(**a) for a in db.execute("SELECT * FROM answers WHERE answers = %s", (self.id,))]

    @staticmethod
    def get_by_id(id, db):
        return Question(db=db, **db.execute("SELECT * FROM questions WHERE id = %s", (id,))[0])

    def get_quizes(self, db):
        return [Quiz.get_by_id(res['quiz'], db) for res in
                db.execute("SELECT quiz FROM quiz_questions WHERE question=%s", (self.id,))]


class Category(object):
    def __init__(self, id, name):
        self.id = int(id)
        self.name = str(name)

    def get_all_questions(self, db):
        return [Question(db=db, **q) for q in
                db.execute("SELECT * FROM questions WHERE category = %s", (self.id,))]

    @staticmethod
    def get_by_id(cat, db):
        return Category(**db.execute("SELECT * FROM categories WHERE id = %s", (cat,))[0])

    @staticmethod
    def fetch_all(db):
        res = db.execute("SELECT * FROM categories")
        categories = []
        for r in res:
            categories.append(Category(**r))
        return categories


class Answer(object):
    def __init__(self, id, correct, answer, answers):
        self.correct = correct
        self.answer = answer
        self.answers = answers
        self.id = id


class Quiz(object):
    def __init__(self, id, name, year, public):
        self.public = public
        self.id = id
        self.name = name
        self.year = year

    def get_ast_index(self, db):
        res = db.execute("SELECT index FROM quiz_questions WHERE quiz=%s ORDER BY index DESC LIMIT 1", (self.id,))
        return res[0]['index'] if len(res) > 0 else 0

    def add(self, question, db):
        db.execute("INSERT INTO quiz_questions (index, question, quiz) VALUES (%s, %s, %s)",
                   (self.get_ast_index(db) + 1, question.id, self.id), True)

    @staticmethod
    def get_by_id(quiz, db):
        return Quiz(**db.execute("SELECT * FROM quizes WHERE id = %s", (quiz,))[0])

    @staticmethod
    def get_all(db):
        return [Quiz(**r) for r in db.execute("SELECT * FROM quizes")]


class DeviceToken(object):
    def __init__(self, id, description, token):
        self.id = id
        self.name = description
        self.token = token

    @staticmethod
    def get_all(db):
        return [DeviceToken(**d) for d in db.execute("SELECT * FROM device_api_tokens")]


class Team(object):
    def __init__(self, id, name, year):
        self.id = id
        self.name = name
        self.year = year

    def get_members(self, db):
        members = db.execute(
            "SELECT id, username, admin, display_name FROM users LEFT JOIN team_memberships ON team_memberships.user = users.id where team_memberships.team = %s",
            (self.id,))
        return [User(**u) for u in members]

    def add_member(self, user, db):
        db.ececute("INSERT INTO team_memberships (team, user) VALUES(%s, %s)", (self.id, user.id), insert=True)

    @staticmethod
    def create(name, year, db):
        db.execute("INSERT INTO teams (name, year) VALUES(%s, %s)", (name, year), insert=True)

    @staticmethod
    def get_all(db):
        res = db.execute("SELECT * FROM teams")
        return [Team(**t) for t in res]


class User(object):
    def __init__(self, id, username, admin, display_name, email):
        self.id = id
        self.username = username
        self.admin = admin
        self.display_name = display_name
        self.email = email

    @staticmethod
    def login(username, password, db):
        m = hashlib.sha512()
        m.update(password.encode('utf-8'))
        res = db.execute("SELECT id, username, admin, display_name FROM users WHERE username=%s AND password=%s",
                         (username, m.hexdigest()))
        if len(res) == 0:
            return None
        return User(**res[0])

    @staticmethod
    def create(username, password, admin, display_name, email, db):
        m = hashlib.sha512()
        m.update(password.encode('utf-8'))
        db.execute("INSERT INTO users (username, password, admin, display_name, email) VALUES (%s, %s, %s, %s, %s)",
                   (username, m.hexdigest(), admin, display_name, email), insert=True)

    @staticmethod
    def get_all(db):
        res = db.execute("SELECT username, admin, display_name, email FROM users")
        return [User(**r) for r in res]


class Display(object):
    def __init__(self, token):
        self.token = token
        self.ready = True
        self.r = True
        self.w = True
