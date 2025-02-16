from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt
from blockchain import Blockchain
from vote_logic import add_vote, count_vote
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

blockchain = Blockchain()

DATABASE = {
    "dbname": "voting_system",
    "user": "voting_user",
    "password": "16189251",
    "host": "localhost",
    "port": 5432
}

def get_db_connection():
    return psycopg2.connect(**DATABASE, cursor_factory = RealDictCursor)

# ----------- DATABASE SETUP (Run once) -----------
with get_db_connection() as conn:
    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(10) CHECK (role IN ('admin', 'voter')) NOT NULL
        );
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );
        ''')
    conn.commit()

# ---------- AUTHENTICATION ENDPOINTS -----------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'voter')

    if role not in ['admin', 'voter']:
        return jsonify({'error':'Invalid role'}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                    (username, hashed_password, role)
                )
            conn.commit()
        return jsonify({'status': 'User registered Successfully'}), 201
    except psycopg2.Error:
        return jsonify({'error': 'Username already exist'}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()

            if user and bcrypt.check_password_hash(user["password"], password):
                access_token = create_access_token(identity=user["username"], additional_claims={"role": user["role"]})
                return jsonify(access_token=access_token), 200
            else:
                return jsonify({'error': 'Invalid Credentials'}), 401

# ---------- ADMIN ENDPOINTS -----------
@app.route('/admin/add-candidate', methods=['POST'])
@jwt_required()
def add_candidate():
    claims = get_jwt()

    if claims.get('role') != 'admin':
        return jsonify({'error':'Unauthorized'}), 403

    candidate_name = request.get_json()['name'] #edited the syntax (not the one given) check the given one for any error
    if not candidate_name:
        return jsonify({'error':'Candidate name Required'}), 400

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO candidates (name) VALUES (%s)", (candidate_name,))
            conn.commit()
            return jsonify({'status': 'Candidate Added Successfully'}), 201
    except psycopg2.Error:
        return jsonify({'error': 'Candidate name already exist'}), 400

# ---------- VOTER ENDPOINTS -----------
@app.route('/voter/cast-vote', methods=['POST'])
@jwt_required()
def casr_vote():
    identity = request.get_json()['identity' ,{}] #edited the syntax (not the one given) check the given one for any error
    role = identity.get('role')
    if role != 'voter':
        return jsonify({'error':'Unauthorized'}), 403

    voter_id = identity.get('username')
    candidate_name = request.get_json()['candidate'] #edited the syntax (not the one given) check the given one for any error
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM candidate WHERE name = %s", (candidate_name,))
            candidate = cur.fetchone()
            if not candidate:
                return jsonify({'error':'Candidate not found'}), 404

    result = add_vote(blockchain, voter_id, candidate_name, [candidate_name])
    return jsonify({"message": result}), 200

# ---------- RESULT ENDPOINTS -----------
@app.route('/result', methods=['GET'])
@jwt_required()
def result():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM candidate")
            candidates = [row["name"]for row in cur.fetchall()]
    vote_count = count_vote(blockchain, candidates)
    return jsonify({'vote_count': vote_count}), 200

# ---------- RUN FLASK SERVER -----------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
