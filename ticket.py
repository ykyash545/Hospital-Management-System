import streamlit as st
import psycopg2
import csv
from io import StringIO

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

# Create groups table if it doesn't exist
create_group_table = """
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
"""
cursor.execute(create_group_table)

# Create tickets table if it doesn't exist
create_ticket_table = """
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Open',
    assigned_to_group INTEGER,
    raised_from_organization VARCHAR(255)  -- Add this line to create the new column
);
"""
cursor.execute(create_ticket_table)
conn.commit()

# Function to close a ticket
def close_ticket(ticket_id):
    cursor.execute("UPDATE tickets SET status = 'Closed' WHERE id = %s", (ticket_id,))
    conn.commit()
    st.success(f"Ticket with ID {ticket_id} closed successfully!")

# Function to edit ticket status
def edit_ticket_status(ticket_id, new_status):
    cursor.execute("UPDATE tickets SET status = %s WHERE id = %s", (new_status, ticket_id))
    conn.commit()
    st.success(f"Ticket with ID {ticket_id} status updated successfully!")

# Function to export ticket details to CSV
def export_tickets():
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    if tickets:
        with StringIO() as buffer:
            writer = csv.writer(buffer)
            writer.writerow(["ID", "Title", "Description", "Status", "Assigned Group", "Raised from Organization"])
            writer.writerows(tickets)
            csv_data = buffer.getvalue()
        st.download_button(label="Export CSV", data=csv_data, file_name="tickets.csv", mime="text/csv")

# Streamlit App
st.title("Alps Help Desk")

# Form to add a new group
new_group_form = st.form("new_group")
group_name = new_group_form.text_input("New Group Name")
add_group_button = new_group_form.form_submit_button("Add Group")

if add_group_button:
    cursor.execute("INSERT INTO groups (name) VALUES (%s)", (group_name,))
    conn.commit()
    st.success(f"Group '{group_name}' added successfully!")

# Form to add a new ticket
new_ticket_form = st.form("new_ticket")
title = new_ticket_form.text_input("Title")
description = new_ticket_form.text_area("Description")

# Function to add a new ticket
def add_ticket(title, description, status, assigned_to_group=None, raised_from_organization=None):
    cursor.execute("INSERT INTO tickets (title, description, status, assigned_to_group, raised_from_organization) VALUES (%s, %s, %s, %s, %s)", (title, description, status, assigned_to_group, raised_from_organization))
    conn.commit()
    st.success("Ticket added successfully!")

# Add a dropdown menu for selecting status
status_options = ("Open", "Pending", "Resolved")
status = new_ticket_form.selectbox("Status", options=status_options)

# Fetch group names
cursor.execute("SELECT name FROM groups")
group_records = cursor.fetchall()
if group_records:
    group_options = [group[0] for group in group_records]
else:
    group_options = []

# Add a dropdown menu for selecting assigned group
assigned_to_group = new_ticket_form.selectbox("Assign to Group", options=[] + group_options)

# Add a dropdown menu for selecting organization
organization_options = ["SOC_DATACENTRE", "External"]  # Update with actual organization names
raised_from_organization = new_ticket_form.selectbox("Raised from Organization", options=organization_options)

submit_button = new_ticket_form.form_submit_button("Submit Ticket")

if submit_button:
    # Get group id if assigned
    if assigned_to_group:
        cursor.execute("SELECT id FROM groups WHERE name = %s", (assigned_to_group,))
        assigned_group_id = cursor.fetchone()
        if assigned_group_id:
            assigned_group_id = assigned_group_id[0]
        else:
            assigned_group_id = None
        add_ticket(title, description, status, assigned_group_id, raised_from_organization)
    else:
        add_ticket(title, description, status, raised_from_organization)


# Form to close a ticket
close_ticket_form = st.form("close_ticket")
close_ticket_id = close_ticket_form.text_input("Enter Ticket ID to Close")
close_button = close_ticket_form.form_submit_button("Close Ticket")

if close_button:
    # Validate input to ensure it's a valid integer
    try:
        ticket_id = int(close_ticket_id)
        close_ticket(ticket_id)
    except ValueError:
        st.error("Invalid ticket ID. Please enter an integer.")

# Form to edit ticket status
edit_status_form = st.form("edit_status")
edit_ticket_id = edit_status_form.text_input("Enter Ticket ID to Edit Status")
new_status_options = ("Open", "Pending", "Resolved", "Closed")
new_status = edit_status_form.selectbox("New Status", options=new_status_options)
edit_button = edit_status_form.form_submit_button("Edit Status")

if edit_button:
    # Validate input to ensure it's a valid integer
    try:
        ticket_id = int(edit_ticket_id)
        edit_ticket_status(ticket_id, new_status)
    except ValueError:
        st.error("Invalid ticket ID. Please enter an integer.")

# Export button to download ticket details
export_tickets()

# Display existing tickets in card-like layout
st.header("Tickets")

cursor.execute("SELECT t.id, t.title, t.description, t.status, COALESCE(g.name, 'Unassigned') AS assigned_group, t.raised_from_organization FROM tickets t LEFT JOIN groups g ON t.assigned_to_group = g.id")
tickets = cursor.fetchall()

if tickets:
    group_tickets = {}
    for ticket in tickets:
        group_name = ticket[4]
        if group_name not in group_tickets:
            group_tickets[group_name] = []
        group_tickets[group_name].append(ticket)

    for group_name, group_tickets_list in group_tickets.items():
        st.subheader(f"Group: {group_name}")
        for ticket in group_tickets_list:
            status_color = ""
            if ticket[3] == "Open":
                status_color = "rgba(102, 204, 102, 0.5)"  # Semi-transparent green
            elif ticket[3] == "Pending":
                status_color = "rgba(255, 204, 0, 0.5)"   # Semi-transparent yellow
            elif ticket[3] == "Resolved":
                status_color = "rgba(207, 52, 118, 0.5)"  # Semi-transparent magenta
            elif ticket[3] == "Closed":
                status_color = "rgba(255, 102, 102, 0.5)" # Semi-transparent red

            st.markdown(
                f"""
                <div style='padding: 7px; border-radius: 5px; background-color: {status_color};'>
                    <h3 style='margin-bottom: 7px;'>Ticket ID: {ticket[0]}</h3>
                    <p><strong>Title:</strong> {ticket[1]}</p>
                    <p><strong>Status:</strong> {ticket[3]}</p>
                    <p><strong>Assigned Group:</strong> {ticket[4]}</p>
                    <p><strong>Raised from Organization:</strong> {ticket[5]}</p>
                    <p><strong>Description:</strong> {ticket[2]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.info("No tickets found.")

cursor.close()
conn.close()
