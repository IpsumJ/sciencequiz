class Question(object):
    def __init__(self, id, question, category, image, db):
        self.id = id
        self.question = question
        self.category = Category.get_by_id(category, db)
        self.answers = [Answer(**a) for a in db.execute("SELECT * FROM answers WHERE answers = %s", (self.id,))]
        self.db = db

    @staticmethod
    def get_by_id(id, db):
        return Question(**db.execute("SELECT * FROM questions WHERE id = %s", (id,))[0], db=db)

    def get_quizes(self):
        return [Quiz.get_by_id(res['quiz'], db=self.db) for res in
                self.db.execute("SELECT quiz FROM quiz_questions WHERE question=%s", (self.id,))]


class Category(object):
    def __init__(self, id, name, db):
        self.id = int(id)
        self.name = str(name)
        self.db = db

    def get_all_questions(self):
        return [Question(**q, db=self.db) for q in
                self.db.execute("SELECT * FROM questions WHERE category = %s", (self.id,))]

    @staticmethod
    def get_by_id(cat, db):
        return Category(**db.execute("SELECT * FROM categories WHERE id = %s", (cat,))[0], db=db)

    @staticmethod
    def fetch_all(db):
        res = db.execute("SELECT * FROM categories")
        categories = []
        for r in res:
            categories.append(Category(**r, db=db))
        return categories


class Answer(object):
    def __init__(self, id, correct, answer, answers):
        self.correct = correct
        self.answer = answer
        self.answers = answers
        self.id = id


class Quiz(object):
    def __init__(self, id, name, year, public, db):
        self.public = public
        self.id = id
        self.name = name
        self.year = year
        self.db = db

    def get_ast_index(self):
        res = self.db.execute("SELECT index FROM quiz_questions WHERE quiz=%s ORDER BY index LIMIT 1", (self.id,))
        return res[0]['index'] if len(res) > 0 else 0

    def add(self, question):
        self.db.execute("INSERT INTO quiz_questions (index, question, quiz) VALUES (%s, %s, %s)",
                        (self.get_ast_index() + 1, question.id, self.id), True)

    @staticmethod
    def get_by_id(quiz, db):
        return Quiz(**db.execute("SELECT * FROM quizes WHERE id = %s", (quiz,))[0], db=db)

    @staticmethod
    def get_all(db):
        return [Quiz(**r, db=db) for r in db.execute("SELECT * FROM quizes")]


class DeviceToken(object):
    def __init__(self, id, description, token, db):
        self.id = id
        self.name = description
        self.token = token

    @staticmethod
    def get_all(db):
        return [DeviceToken(**d, db=db) for d in db.execute("SELECT * FROM device_api_tokens")]
