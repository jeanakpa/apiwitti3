from extensions import db

class MyWittiJetonsCalculState(db.Model):
    __tablename__ = 'mywitti_jetons_calcul_state'
    customer_code = db.Column(db.String(50), primary_key=True)
    last_calculated = db.Column(db.Date)
    reliquat_depot = db.Column(db.BigInteger, default=0)
    reliquat_retrait = db.Column(db.BigInteger, default=0)
    last_stability_calculated = db.Column(db.Date)
    reliquat_stabilite = db.Column(db.BigInteger, default=0)
    total_jetons_transaction = db.Column(db.BigInteger, default=0)
    total_jetons_stabilite = db.Column(db.BigInteger, default=0) 