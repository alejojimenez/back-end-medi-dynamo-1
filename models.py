from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    username = db.Column(db.String(60), nullable=True, unique=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username

    def serialize(self):
        return {
            "email":self.email,
            "username":self.username,
            "name":self.name,
            "id":self.id
        }

class Patients(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rut = db.Column(db.String(10), nullable=False )
    firstname = db.Column(db.String(80), nullable=False )
    lastname = db.Column(db.String(80), nullable=False )
    address = db.Column(db.String(100), nullable=False )
    telephone = db.Column(db.String(15), nullable=False )
    age = db.Column(db.String(3), nullable=False )
    sex = db.Column(db.String(15), nullable=False )
    forecast = db.Column(db.String(50), nullable=False )

    def __repr__(self):
        return "<Patients %r>" % self.rut

    def serialize(self):
        return {
            "id": self.id,
            "rut": self.rut,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "address": self.address,
            "telephone": self.telephone,
            "age": self.age,
            "sex": self.sex,
            "forecast": self.forecast
        }
