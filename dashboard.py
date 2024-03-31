import streamlit as st
import psycopg2
import pandas as pd
import subprocess
import plotly.express as px
from streamlit_metrics import metric

# Database connection details (replace with yours)
DB_HOST = "project1-apls-admin.a.aivencloud.com"
DB_NAME = "defaultdb"
DB_USER = "avnadmin"
DB_PASSWORD = "AVNS_EFgGG4-VjJtgSflszpI"
PORT="15883"

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    port=PORT
)

# Create tables if they don't exist (modify as needed)
cursor = conn.cursor()

create_ticket_table = """
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Open',
    assigned_to_group INTEGER
);
"""

cursor.execute(create_ticket_table)

create_group_table = """
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
"""
cursor.execute(create_group_table)

# Function to add a new ticket
def add_ticket(title, description, status, assigned_to_group=None):
    cursor.execute("INSERT INTO tickets (title, description, status, assigned_to_group) VALUES (%s, %s, %s, %s)", (title, description, status, assigned_to_group))
    conn.commit()
    st.success("Ticket added successfully!")

# Function to close a ticket
def close_ticket(ticket_id):
    cursor.execute("UPDATE tickets SET status = 'Closed' WHERE id = %s", (ticket_id,))
    conn.commit()
    st.success(f"Ticket with ID {ticket_id} closed successfully!")

# Function to fetch ticket counts for different statuses
def get_ticket_counts():
    cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
    data = cursor.fetchall()
    counts = {status: count for status, count in data}
    return counts

# Function to count the total number of appointments
def count_appointments():
    cursor.execute("SELECT COUNT(*) FROM appointments")
    total_appointments = cursor.fetchone()[0]
    return total_appointments

# Streamlit App
st.title("Dashboard")

# Create a row for buttons
button_col1, button_col2, button_col3 = st.columns(3)

# Add admin button
if button_col1.button("Admin"):
    # Add admin functionality here
    st.write("Admin Panel")
    # For example, you can add options to manage users, groups, etc.
    subprocess.Popen(["streamlit", "run", "main.py"])

# Add appointment button
if button_col2.button("Appointments"):
    # Add appointment functionality here
    st.write("Appointment Panel")
    # For example, you can add options to manage appointments
    subprocess.Popen(["streamlit", "run", "appointment.py"])

# Redirect to ticket system dashboard if "Open Tickets" is selected
if button_col3.button("Open Tickets"):
    st.write("Redirecting to Ticket System Dashboard...")
    # Redirect logic goes here
    subprocess.Popen(["streamlit", "run", "ticket.py"])

# Analytics options
selected_analytics = st.sidebar.selectbox("Select Analytics", ("Ticket Status Distribution",))

# Fetching data for selected analytics
if selected_analytics == "Ticket Status Distribution":
    counts = get_ticket_counts()
    st.write("")
    
    # Use st.columns instead of st.beta_columns
    columns = st.columns(len(counts) + 1)
    for i, (status, count) in enumerate(counts.items()):
        with columns[i]:
            metric(status, count)
    
    # Add the total appointments metric
    with columns[-1]:
        total_appointments = count_appointments()
        metric("Total Appointments", total_appointments)

    cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['Status', 'Count'])

    # Change color of open tickets to green and closed tickets to red
    colors = {'Open': 'green', 'Closed': 'red'}
    df['Color'] = df['Status'].map(colors)

    # Create bar chart
    fig1 = px.bar(df, x='Status', y='Count', title='Ticket Status Distribution', color='Color',
                  category_orders={'Status': ['Open', 'Closed']})

    # Create pie chart
    fig2 = px.pie(df, values='Count', names='Status', title='Ticket Status Distribution', hole=0.8)

    # Create two columns for placing the charts side by side
    col1, col2 = st.columns(2)

    # Display charts side by side
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

cursor.close()
conn.close()
