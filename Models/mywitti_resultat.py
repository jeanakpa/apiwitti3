from extensions import db
from Models.mywitti_users import MyWittiUser
from Models.mywitti_client import MyWittiClient
from Models.mywitti_category import MyWittiCategory

class MyWittiResultatCriteria(db.Model):
    __tablename__ = 'mywitti_resultat_criteria'
    id = db.Column(db.BigInteger, primary_key=True)
    criteria_name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<ResultatCriteria {self.criteria_name}>"

class MyWittiResultatTotal(db.Model):
    __tablename__ = 'mywitti_resultat_total'
    id = db.Column(db.BigInteger, primary_key=True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    customer = db.relationship('MyWittiClient', backref='resultat_totals')

    def __repr__(self):
        return f"<ResultatTotal {self.customer_id} - {self.date}>"

class MyWittiResultatPoint(db.Model):
    __tablename__ = 'mywitti_resultat_point'
    id = db.Column(db.BigInteger, primary_key=True)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id'), nullable=False)
    notation = db.Column(db.String(255), nullable=False)
    jeton = db.Column(db.Integer, nullable=False)
    mois = db.Column(db.String(50), nullable=False)
    montant = db.Column(db.BigInteger, nullable=False)
    date_notes = db.Column(db.Date, nullable=False)
    customer = db.relationship('MyWittiClient', backref='resultat_points')

    def __repr__(self):
        return f"<ResultatPoint {self.customer_id} - {self.mois}>"

class MyWittiClientRecompense(db.Model):
    __tablename__ = 'mywitti_client_recompense'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_users.id'), nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    category_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_category.id'))
    user = db.relationship('MyWittiUser', backref='recompenses')
    customer = db.relationship('MyWittiClient', backref='client_recompenses')
    category = db.relationship('MyWittiCategory', backref='recompenses')

    def __repr__(self):
        return f"<ClientRecompense {self.customer_id} - {self.score}>" 