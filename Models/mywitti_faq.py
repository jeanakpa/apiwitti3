from extensions import db

class MyWittiFAQ(db.Model):
    __tablename__ = 'mywitti_faq'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer
        } 