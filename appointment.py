import streamlit as st
import psycopg2

# Function to connect to PostgreSQL database
def connect_to_db():
    conn = psycopg2.connect(
        host="project1-apls-admin.a.aivencloud.com",
        database="defaultdb",
        user="avnadmin",
        password="AVNS_EFgGG4-VjJtgSflszpI",
        port="15883"
    )
    return conn

# Function to create appointments table if not exists
def create_appointments_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            date DATE,
            time TIME,
            illness VARCHAR(255),
            doctor VARCHAR(255)
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert appointment details into the database
def insert_appointment(name, date, time, illness, doctor):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO appointments (name, date, time, illness, doctor) VALUES (%s, %s, %s, %s, %s)",
                   (name, date, time, illness, doctor))
    conn.commit()
    conn.close()

# Function to display existing appointments
def display_appointments():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    appointments = cursor.fetchall()
    conn.close()
    return appointments

# Function to get distinct doctor names from the appointments table
def get_doctor_list():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT name FROM doctors")
    doctors = cursor.fetchall()
    conn.close()
    return [doctor[0] for doctor in doctors]

# Streamlit UI
def main():
    st.title("Appointment Scheduler")

    # Create appointments table if not exists
    create_appointments_table()

    # Schedule appointment
    st.header("Schedule Appointment")
    name = st.text_input("Name:")
    date = st.date_input("Date:")
    time = st.time_input("Time:")
    illness = st.text_input("Illness:")
    doctor_list = get_doctor_list()
    doctor = st.selectbox("Doctor:", options=doctor_list)

    if st.button("Schedule"):
        insert_appointment(name, date, time, illness, doctor)
        st.success("Appointment scheduled successfully!")

    # Display existing appointments
    st.header("Existing Appointments")
    appointments = display_appointments()
    if appointments:
        for appointment in appointments:
            st.markdown(
                f"""
                <div style='background-color: #D0F0C0; border: 1px solid #e6e6e6; border-radius: 5px; padding: 10px; margin-bottom: 10px;'>
                    <p><strong>Appointment ID:</strong> {appointment[0]}</p>
                    <p><strong>Name:</strong> {appointment[1]}</p>
                    <p><strong>Date:</strong> {appointment[2]}</p>
                    <p><strong>Time:</strong> {appointment[3]}</p>
                    <p><strong>Illness:</strong> {appointment[4]}</p>
                    <p><strong>Doctor:</strong> {appointment[5]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.info("No appointments scheduled yet.")

if __name__ == "__main__":
    main()