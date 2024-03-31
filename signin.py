import streamlit as st
import psycopg2
import subprocess
from passlib.hash import pbkdf2_sha256

# Function to connect to the PostgreSQL database
def connect_to_db():
    conn = psycopg2.connect(
        dbname="defaultdb",
        user="avnadmin",
        password="AVNS_EFgGG4-VjJtgSflszpI",
        host="project1-apls-admin.a.aivencloud.com",
        port="15883"  
    )
    return conn

# Function to create the users table if it doesn't exist
def create_users_table(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL
        );
    ''')
    conn.commit()
    cursor.close()

# Function to insert a new user into the database
def insert_user(conn, username, password, email):
    hashed_password = pbkdf2_sha256.hash(password)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, password, email)
        VALUES (%s, %s, %s);
    ''', (username, hashed_password, email))
    conn.commit()
    cursor.close()

def verify_password(password, hashed_password):
    return pbkdf2_sha256.verify(password, hashed_password)

def main():
    # Add logo (replace "logo.png" with your logo file path)
    st.image("D:\Back up 2024 Jan\ALPS PROJECT\Admin Portal\Deployed\Portal\logo.jpg", width=250)  # You can adjust the width as needed

    st.title("Let's Get Started:")
    st.title("Sign in into portal")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")

    if st.button("Sign In"):
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        hashed_password = cursor.fetchone()
        cursor.close()
        conn.close()

        if hashed_password and verify_password(password, hashed_password[0]):
            st.success("Successfully signed in!")
            # Redirect or perform actions after successful sign-in
            subprocess.Popen(["streamlit", "run", "dashboard.py"])
        else:
            st.error("Invalid username or password. Please try again.")
            raise ValueError("Invalid username or password")  # Throw exception for invalid credentials

    if st.button("Register"):
        conn = connect_to_db()
        create_users_table(conn)

        # Check if username or email already exists
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            st.error("Username or email already exists. Please choose another one.")
        else:
            insert_user(conn, username, password, email)
            st.success("User registered successfully. You can now sign in.")

if __name__ == "__main__":
    main()
