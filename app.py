from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from firebase_admin import credentials, initialize_app, firestore
from flask_session import Session
import os
import base64
class User:
    def __init__(self, id_,username, email, image) -> None:
        self.id_ = id_
        self.username = username
        self.email = email 
        self.image = image
        
        


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = '122782'
app.config['SESSION_TYPE'] = 'filesystem'  # Configura el tipo de sesión (en este caso, se guarda en el sistema de archivos)
Session(app)





# Initialize Firebase Admin with the credentials
cred = credentials.Certificate("api/key.json")
default_app = initialize_app(cred)

# Initialize Firestore DB
db = firestore.client()

@app.route('/')
def home():
    return render_template('index.html')




def get_next_user_id():
    # Get all documents in the 'users' collection
    users = db.collection('users').get()
    # Count the number of documents
    user_count = len(users)
    # The next user ID is the current count + 1
    return user_count + 1

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        # Generate the next user ID
        id_ = get_next_user_id()
        name = request.form['name']
        pasw = request.form['password']
        email = request.form['email']
        if 'fileInput' in request.files:
            file = request.files['fileInput']
            if file.filename != '':
                # Leer el contenido del archivo y convertirlo a base64
                image_base64 = base64.b64encode(file.read()).decode('utf-8')
        image = image_base64 

        # Create user data
        data = {'id':id_,'username': name, 'password': int(pasw), 'email': str(email),'image': image}
        
        # Add user data to Firestore
        user_ref = db.collection('users').add(data)
        
        # Redirect to success page
        return redirect(url_for('success'))
    except Exception as e:
        return jsonify({"error": f"An Error Occurred: {e}"}), 500



@app.route('/login', methods=['POST'])
def login():
    try:
        # Extract data from the form
        username = request.form['username']
        password = request.form['password']

        # Query Firestore for user
        user_ref = db.collection('users')
        query = user_ref.where('username', '==', username).where('password', '==', int(password)).stream()

        # Check if user exists
        user_exists = False
        for user in query:
            user_exists = True
            user_data = user.to_dict()
            logged_in_user = User(
                id_=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                image=user_data['image']
            )
            break

        if user_exists:
            # Store user data in session
            session['logged_in_user'] = logged_in_user.__dict__
            return redirect(url_for('primary'))
        else:
            session['login_error'] = 'User not found or incorrect password'
            return redirect(url_for('login_enter'))  # Redirigir de vuelta al formulario de login
    except Exception as e:
        return jsonify({"error": f"An Error Occurred: {e}"}), 500



@app.route('/login')
def gologin():
    session['login_error'] = None 
    return render_template('login.html')
@app.route('/login_enter')
def login_enter():
    return render_template('login.html')

@app.route('/success')
def success():
    return render_template('success.html')


@app.route('/primary')
def primary():
    if 'logged_in_user' in session:
        user_data = session['logged_in_user']
        return render_template('primary.html', username=user_data['username'], image=user_data['image'])
    else:
        return render_template('primary.html', username='Guest')

if __name__ == '__main__':
    app.run(debug=True)

