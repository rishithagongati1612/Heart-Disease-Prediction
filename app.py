from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import numpy as np
import pickle
from datetime import datetime
from flask_dance.contrib.google import make_google_blueprint, google
from flask_mail import Mail, Message

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mvinod4284@gmail.com'  
app.config['MAIL_PASSWORD'] = 'Mvinod@4284007'  
app.config['MAIL_DEFAULT_SENDER'] = '21p61a05g2@vbithyd.ac.in'  

mail = Mail(app)

# Load the trained model and scaler
model = pickle.load(open('model.pkl', 'rb'))
scaler = pickle.load(open('scaler.pkl', 'rb'))

# User data for demonstration purposes
users = {
    "testuser": "password123"  # Replace this with your database or user management system
}

# Food and exercise recommendations
food_recommendations = {
    0: ["Oatmeal", "Fruits", "Vegetables", "Whole grains", "Nuts"],
    1: ["Salmon", "Avocados", "Quinoa", "Leafy greens", "Dark chocolate"]
}

exercise_recommendations = {
    0: ["Walking", "Yoga", "Swimming", "Cycling"],
    1: ["Running", "HIIT", "Weight training", "Aerobics"]
}

# Add health tips
health_tips = {
    0: [
        "Maintain a balanced diet rich in fruits, vegetables, whole grains, and lean proteins.",
        "Engage in at least 150 minutes of moderate aerobic activity each week.",
        "Stay hydrated by drinking plenty of water throughout the day.",
        "Limit sodium intake to help manage blood pressure.",
        "Get adequate sleep, aiming for 7-9 hours per night.",
        "Avoid smoking and limit alcohol consumption.",
        "Manage stress through relaxation techniques such as yoga or meditation."
    ],
    1: [
        "Consult a healthcare provider for personalized advice.",
        "Adhere to a heart-healthy diet, focusing on low-fat, low-sodium options.",
        "Engage in regular physical activity, as advised by your doctor.",
        "Monitor your blood pressure and cholesterol levels regularly.",
        "Keep a healthy weight and manage your stress levels.",
        "Take prescribed medications as directed and follow up with your doctor.",
        "Consider joining a support group to share experiences and gain motivation."
    ]
}

# Set up Google OAuth
google_bp = make_google_blueprint(
    client_id='YOUR_GOOGLE_CLIENT_ID',  # Replace with your Google Client ID
    client_secret='YOUR_GOOGLE_CLIENT_SECRET',  # Replace with your Google Client Secret
    redirect_to='google_callback'
)
app.register_blueprint(google_bp, url_prefix='/google_login')

@app.route('/')
def home():
    user = session.get('user')
    if isinstance(user, dict):  # Check if user is a dictionary
        return f"Hello, {user.get('name', 'User')}! <a href='/logout'>Logout</a>"
    return render_template('index.html')  # Render index.html for user input

@app.route("/home")
def home_page():
    return render_template("home.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    msg = Message(subject=f'New Contact Form Submission from {name}',
                  recipients=['21p61a05g2@vbithyd.ac.in'],  # Replace with your recipient email
                  body=f'Name: {name}\nEmail: {email}\nMessage: {message}')

    try:
        mail.send(msg)
        flash("Your message has been sent successfully!")
    except Exception as e:
        flash(f"An error occurred: {str(e)}")
    
    return redirect(url_for('success'))

@app.route('/success')
def success():
    return "Your message has been sent successfully!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        if username in users and users[username] == password:
            session['user'] = {'name': username}
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid Credentials")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if username in users:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for('signup'))

        users[username] = password
        flash("Account created successfully! You can now log in.")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/auth/google')
def google_login():
    return redirect(url_for('google.login'))

@app.route('/auth/google/callback')
def google_callback():
    if not google.authorized:
        return 'Access denied.'

    resp = google.get('/plus/v1/people/me')
    if resp.ok:
        session['user'] = resp.json()  
        return redirect(url_for('home'))
    return 'Failed to fetch user information.'

@app.route('/predict', methods=['POST'])
def predict():
    name = request.form.get('name')
    age = request.form.get('age')

    # Get the input data from the form
    features = [float(x) for x in request.form.values()]

    # Convert the input into an array and scale it
    final_features = [np.array(features[:-2])]  # Exclude dietary and activity level for prediction
    final_features_scaled = scaler.transform(final_features)

    # Make a prediction using the loaded model
    prediction = model.predict(final_features_scaled)

    # Output based on prediction
    if prediction == 0:
        output = 'No Heart Disease detected. You do not need to consult a doctor.'
        food = food_recommendations[0]
        exercises = exercise_recommendations[0]
        tips = health_tips[0]
        risk_no = 1  # Example data
        risk_moderate = 0
        risk_high = 0
    else:
        output = 'Heart Disease detected. It is advised to consult a doctor immediately.'
        food = food_recommendations[1]
        exercises = exercise_recommendations[1]
        tips = health_tips[1]
        risk_no = 0
        risk_moderate = 1  # Example data
        risk_high = 0

    current_date = datetime.now().strftime('%Y-%m-%d')  # Get current date

    # Save the prediction result to a text file for download
    result_filename = 'prediction_result.txt'
    with open(result_filename, 'w') as f:
        f.write(f"Name: {name}\n")
        f.write(f"Age: {age}\n")
        f.write(f"Prediction: {output}\n\n")
        f.write('Food Recommendations:\n')
        f.write('\n'.join(food) + '\n\n')
        f.write('Exercise Recommendations:\n')
        f.write('\n'.join(exercises) + '\n\n')
        f.write('Health Tips:\n')
        f.write('\n'.join(tips))

    return render_template('result.html', 
                           prediction_text=output, 
                           heart_condition='Moderate Risk' if prediction == 1 else 'No Risk',
                           food_recommendations=food, 
                           exercise_recommendations=exercises, 
                           health_tips=tips,
                           name=name,
                           age=age,
                           current_date=current_date,
                           result_file=result_filename,
                           risk_no=risk_no,
                           risk_moderate=risk_moderate,
                           risk_high=risk_high)

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    return send_file(filename, as_attachment=True)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
