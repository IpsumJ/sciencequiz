import sciencequiz


class Question(object):
    def __init__(self, res):
        pass


class Category(object):
    def __init__(self, id, name, db):
        self.id = int(id)
        self.name = str(name)
        self.db = db

    def get_all_questions(self):
        return self.db.execute("SELECT * FROM questions WHERE category = %s", (self.id,))
