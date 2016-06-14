import sciencequiz


class Question(object):
    def __init__(self, id, question, category, image, db):
        self.id = id
        self.question = question
        self.category = Category.get_by_id(category, db)


class Category(object):
    def __init__(self, id, name, db):
        self.id = int(id)
        self.name = str(name)
        self.db = db

    def get_all_questions(self):
        print(self.db.execute("SELECT * FROM questions WHERE category = %s", (self.id,)))
        return [Question(**q, db=self.db) for q in
                self.db.execute("SELECT * FROM questions WHERE category = %s", (self.id,))]

    @staticmethod
    def get_by_id(cat, db):
        res = db.execute("SELECT * FROM categories WHERE id = %s", (cat,))
        print(res)
        return Category(**res[0], db=db)
