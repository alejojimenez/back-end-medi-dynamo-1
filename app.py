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

## Permite conectar la BD MySQL
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:X3#stejen@127.0.0.1:3306/medidynamo" 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = True
app.config["ENV"] = "development"
app.config["SECRET_KEY"] = "secret_key"
app.config["JWT_SECRET_KEY"] = 'encrypt'
## Permite instanciar de manera local la BD MySQL
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

#######################################
##        SIGNUP - REGISTRARSE       ##
#######################################
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

######################################
##          SIGNIN - LOGIN          ##
######################################
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
            "expires": expiracion.total_seconds()*1000,
            "msg": "Success"
        }

        return jsonify(data), 200

###############################################################
##                       CREATE = POST                       ##
###############################################################
@app.route('/api/medidynamo/create/patients', methods=['POST'])
def create_patients():
    cur = mysql.connection.cursor()
    rut = request.get_json()['rut']
    firstname = request.get_json()['firstname']
    lastname = request.get_json()['lastname']
    address = request.get_json()['address']
    telephone = request.get_json()['telephone']    
    age = request.get_json()['age']
    sex = request.get_json()['sex']
    email = request.get_json()['email']
    forecast = request.get_json()['forecast']
    
    cur.execute("INSERT INTO patients (rut, firstname, lastname, address, telephone, age, sex, email, forecast) VALUES ('" +
            str(rut) + "', '" +
            str(firstname) + "', '" +
            str(lastname) + "', '" +
            str(address) + "', '" +
            str(telephone) + "', '" +
            str(age) + "', '" +
            str(sex) + "', '" +
            str(email) + "', '" +
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
        'email' : email,
        'forecast' : forecast
    }

    return jsonify({'result' : result})

############################################################
##                       READ = GET                       ##
############################################################
@app.route('/api/medidynamo/read/patients', methods=['GET'])
def read_patients():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM patients")
    row_headers = [x[0]
        for x in cur.description] # this will extract row headers
    dataPatients = cur.fetchall()
    json_data = []

    for result in dataPatients:
        json_data.append(dict(zip(row_headers, result)))
    return jsonify(json_data)

#######################################################################
##                            UPDATE = PUT                           ##
#######################################################################
@app.route('/api/medidynamo/update/patient/<int:id>', methods=['PUT'])
def update_patient(id):
    if request.method == 'PUT':
        cur = mysql.connection.cursor()
        rut = request.get_json()['rut']
        firstname = request.get_json()['firstname']
        lastname = request.get_json()['lastname']
        address = request.get_json()['address']
        telephone = request.get_json()['telephone']
        age = request.get_json()['age']
        sex = request.get_json()['sex']
        email = request.get_json()['email']
        forecast = request.get_json()['forecast']
        cur.execute("""
            UPDATE patients
            SET rut = %s,
                firstname = %s,
                lastname = %s,
                address = %s,
                telephone = %s,
                age = %s,
                sex = %s,
                email = %s,
                forecast = %s
            WHERE id=%s
            """, (rut, firstname, lastname, address, telephone, age, sex, email, forecast, id,))
        mysql.connection.commit()
        result = {
            'rut': rut,
            'firstname': firstname,
            'lastname': lastname,
            'address': address,
            'telephone': telephone,
            'age': age,
            'sex': sex,
            'email': email,
            'forecast': forecast
        }
    return jsonify({'result': result})

##########################################################################
##                             DELETE = DELETE                          ##
##########################################################################
@app.route('/api/medidynamo/delete/patient/<int:id>', methods=['DELETE'])
def delete_patient(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM patients WHERE id=%s', (id,))
    mysql.connection.commit()
    print(id)
    return jsonify({"id": id})


if __name__ == "__main__":
    manager.run()
