from extensions import db
from datetime import datetime

class MyWittiSurvey(db.Model):
    __tablename__ = 'mywitti_survey'
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Survey {self.id} - {self.title}>"

class MyWittiSurveyOption(db.Model):
    __tablename__ = 'mywitti_survey_option'
    id = db.Column(db.BigInteger, primary_key=True)
    survey_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_survey.id'), nullable=False)
    option_text = db.Column(db.String(50), nullable=False)
    option_value = db.Column(db.Integer, nullable=False)
    survey = db.relationship('MyWittiSurvey', backref='options')

    def __repr__(self):
        return f"<SurveyOption {self.option_value} - {self.option_text}>"

class MyWittiSurveyResponse(db.Model):
    __tablename__ = 'mywitti_survey_response'
    id = db.Column(db.BigInteger, primary_key=True)
    survey_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_survey.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_users.id'), nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_client.id'), nullable=False)
    option_id = db.Column(db.BigInteger, db.ForeignKey('mywitti_survey_option.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    survey = db.relationship('MyWittiSurvey', backref='responses')
    option = db.relationship('MyWittiSurveyOption', backref='responses')
    user = db.relationship('MyWittiUser', backref='basic_survey_responses')
    customer = db.relationship('MyWittiClient', backref='basic_survey_responses')

    def __repr__(self):
        return f"<SurveyResponse {self.id} - Survey {self.survey_id}>" 