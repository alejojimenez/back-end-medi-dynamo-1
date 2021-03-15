import os
import re
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
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

app.config['MYSQL_HOST'] = '127.0.0.1' 
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PASSWORD'] = 'X3#stejen' 
app.config['MYSQL_DB'] = 'medidynamo' 


db.init_app(app)
Migrate(app, db)
manager = Manager(app)
manager.add_command("db", MigrateCommand)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
mysql = MySQL(app)
CORS(app)

# Registrase
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

# Login
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

# POST
@app.route('/patients', methods=['POST'])
def create_patients():
    cur = mysql.connection.cursor()
    rut = request.get_json()['rut']
    firstname = request.get_json()['firstname']
    lastname = request.get_json()['lastname']
    address = request.get_json()['address']
    telephone = request.get_json()['telephone']    
    age = request.get_json()['age']
    sex = request.get_json()['sex']
    forecast = request.get_json()['forecast']
    
    cur.execute("INSERT INTO patients (rut, firstname, lastname, address, telephone, age, sex, forecast) VALUES ('" +
            str(rut) + "', '" +
            str(firstname) + "', '" +
            str(lastname) + "', '" +
            str(address) + "', '" +
            str(telephone) + "', '" +
            str(age) + "', '" +
            str(sex) + "', '" +                                                
            str(forecast) + "')")
    mysql.connection.commit()

    result = {
        'rut' : rut,
        'firstname' : firstname,
        'lastname' : lastname,
        'address' : address,
        'telephone' : telephone,
        'age' : age,
        'sex' : sex,
        'forecast' : forecast
    }

    return jsonify({'result' : result})

# GET
@app.route('/api/get_notification', methods=['GET'])
def get_notification():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notification")
    row_headers = [x[0]
        for x in cur.description] # this will extract row headers
    dataNotification = cur.fetchall()
    json_data = []

    for result in dataNotification:
        json_data.append(dict(zip(row_headers, result)))
    return jsonify(json_data)

# PUT
@app.route('/api/update_notification/<int:id>', methods=['PUT'])
def updateNotification(id):
    if request.method == 'PUT':
        cur = mysql.connection.cursor()
        status = request.get_json()['status']
        cur.execute("""
                UPDATE notification
                SET status = %s
                WHERE notificationId=%s
            """, (status, id,))
        mysql.connection.commit()
        result = {
            'status': status
        }
    return jsonify({'result': result})

if __name__ == "__main__":
    manager.run()
