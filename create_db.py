import sqlite3

def create_db():
    # Connect to the SQLite database (it will create the database if it doesn't exist)
    conn = sqlite3.connect('heart_disease_prediction.db')
    cursor = conn.cursor()

    # Create the user_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            sex TEXT NOT NULL,
            diet TEXT NOT NULL,
            activity_level TEXT NOT NULL,
            cp INTEGER,
            trestbps INTEGER,
            chol INTEGER,
            fbs INTEGER,
            restecg INTEGER,
            thalach INTEGER,
            exang INTEGER,
            oldpeak REAL,
            slope INTEGER,
            ca INTEGER,
            thal INTEGER
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()

# Run the function to create the database and table
create_db()
