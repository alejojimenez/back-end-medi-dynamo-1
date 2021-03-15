import os
import re
from flask import Flask, jsonify, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from models import User, db
import datetime

## Permite hacer las encripciones de contraseñas
from werkzeug.security import generate_password_hash, check_password_hash

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:X3#stejen@127.0.0.1:3306/medidynamo" 

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.config["ENV"] = "development"
app.config["SECRET_KEY"] = "secret_key"
app.config["JWT_SECRET_KEY"] = 'encrypt'

db.init_app(app)
Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app)

@app.route('/signup', methods=["POST"])
def signup():
    if request.method == 'POST':
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        ## Validar datos suministrados
        if not email:
            return jsonify({"msg": "Email is required"}), 400
        if not password:
            return jsonify({"msg": "Password is required"}), 400
        ## Validar usuario existente
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"msg": "Username already exists"}), 400
        ## Serializar usuario
        user = User()
        user.email = email
        hashed_password = generate_password_hash(password)
        print(password, hashed_password)
        ## Encriptar password de usuario
        user.password = hashed_password
        user.username = request.json.get("username", None)
        user.name = request.json.get("name")
        ## Adicionar nuevo usuario registrado
        db.session.add(user)
        db.session.commit()

        return jsonify({"success": "Thanks. your register was successfully", "status": "true"}), 200

@app.route('/login', methods=["POST"])
def login():
    if request.method == 'POST':
        username = request.json.get("username", None)
        email = request.json.get("email", None)
        password = request.json.get("password", None)
        ## Validar datos suministrados
        if not username:
            return jsonify({"msg": "Username is required"}), 400
        if not email:
            return jsonify({"msg": "Email is required"}), 400
        if not password:
            return jsonify({"msg": "Password is required"}), 400
        ## Validar usuario existente
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"msg": "Username/Password are incorrect"}), 401
        if not check_password_hash(user.password, password):
            return jsonify({"msg": "Username/Password are incorrect"}), 401
        # crear el token
        expiracion = datetime.timedelta(days=3)
        access_token = create_access_token(identity=user.email, expires_delta=expiracion)
        ## Serializar datos del usuario
        data = {
            "user": user.serialize(),
            "token": access_token,
            "expires": expiracion.total_seconds()*1000
        }

        return jsonify(data), 200

if __name__ == "__main__":
    manager.run()
