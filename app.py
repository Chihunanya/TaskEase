# app.py 

import streamlit as st
import sqlite3
from datetime import datetime, date
import bcrypt

# -----------------------
# Database Setup
# -----------------------
conn = sqlite3.connect("taskease.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    deadline DATE,
    status TEXT DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
""")
conn.commit()

# -----------------------
# Helper Functions
# -----------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode(), password_hash)

def add_user(username, email, password):
    try:
        c.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                  (username, email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def authenticate_user(username, password):
    c.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
    user = c.fetchone()
    if user and verify_password(password, user[1]):
        return user[0]
    return None

def add_task(user_id, title, description, category, deadline):
    c.execute("""INSERT INTO tasks (user_id, title, description, category, deadline) 
                 VALUES (?, ?, ?, ?, ?)""",
              (user_id, title, description, category, deadline))
    conn.commit()

def get_tasks(user_id):
    c.execute("SELECT id, title, description, category, deadline, status FROM tasks WHERE user_id=? ORDER BY deadline ASC", (user_id,))
    return c.fetchall()

def update_task_status(task_id, status):
    c.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
    conn.commit()

# -----------------------
# Streamlit App
# -----------------------
st.set_page_config(page_title="Taskease", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None

# -----------------------
# Login / Signup
# -----------------------
if not st.session_state.logged_in:
    st.title("📝 Taskease - Student Task Manager")
    auth_tab = st.tabs(["Login", "Sign Up"])

    with auth_tab[0]:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user_id = authenticate_user(username, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

    with auth_tab[1]:
        st.subheader("Sign Up")
        new_username = st.text_input("Username", key="signup_user")
        new_email = st.text_input("Email")
        new_password = st.text_input("Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if add_user(new_username, new_email, new_password):
                st.success("Account created! You can login now.")
            else:
                st.error("Username or email already exists.")

# -----------------------
# Dashboard
# -----------------------
else:
    st.sidebar.title("📊 Dashboard")
    menu = st.sidebar.radio("Menu", ["View Tasks", "Add Task", "Analytics", "Logout"])

    if menu == "View Tasks":
        st.header("📋 Your Tasks")
        tasks = get_tasks(st.session_state.user_id)
        today = date.today()

        # Sidebar Summary
        st.sidebar.subheader("📌 Upcoming Tasks")
        upcoming_tasks = [t for t in tasks if t[5]=="Pending" and t[4] and datetime.strptime(t[4], "%Y-%m-%d").date() >= today]
        if upcoming_tasks:
            for t in upcoming_tasks[:5]:  # show next 5 tasks
                st.sidebar.markdown(f"- {t[1]} (Due: {t[4]})")
        else:
            st.sidebar.write("No upcoming tasks!")

        # Search / Filter
        st.sidebar.subheader("🔍 Filter Tasks")
        categories = list(set([t[3] for t in tasks]))
        selected_category = st.sidebar.selectbox("Category", ["All"] + categories)
        status_options = ["All", "Pending", "Completed"]
        selected_status = st.sidebar.selectbox("Status", status_options)

        # Filter tasks
        filtered_tasks = tasks
        if selected_category != "All":
            filtered_tasks = [t for t in filtered_tasks if t[3] == selected_category]
        if selected_status != "All":
            filtered_tasks = [t for t in filtered_tasks if t[5] == selected_status]

        # Overall Progress
        total_tasks = len(filtered_tasks)
        completed_tasks = len([t for t in filtered_tasks if t[5]=="Completed"])
        progress = (completed_tasks / total_tasks) if total_tasks > 0 else 0
        st.subheader("📊 Progress")
        st.progress(progress)

        # Display tasks as cards
        if filtered_tasks:
            for task in filtered_tasks:
                task_id, title, description, category, deadline, status = task

                # Notification and color
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d").date() if deadline else None
                notif = ""
                color = "#080808"
                if deadline_date and status == "Pending":
                    if deadline_date < today:
                        notif = "⛔ Overdue"
                        color = "#080808"
                    elif deadline_date == today:
                        notif = "⚡ Due Today"
                        color = "#181817"

                # Card layout
                with st.container():
                    st.markdown(f"""
                    <div style="
                        background-color:{color};
                        padding:20px;
                        border-radius:12px;
                        margin-bottom:15px;
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                    ">
                        <h3 style="margin-bottom:5px;">{title} {notif}</h3>
                        <p><strong>Category:</strong> {category}</p>
                        <p><strong>Deadline:</strong> {deadline if deadline else 'No deadline'}</p>
                        <details>
                            <summary><strong>Description</strong></summary>
                            <p>{description}</p>
                        </details>
                    </div>
                    """, unsafe_allow_html=True)

                    # Status dropdown
                    status_option = st.selectbox(
                        "Status", ["Pending", "Completed"],
                        index=0 if status=="Pending" else 1, key=f"status_{task_id}"
                    )
                    if status_option != status:
                        update_task_status(task_id, status_option)
                        st.success(f"Updated '{title}' status to {status_option}")

        else:
            st.info("No tasks match your filter.")

    elif menu == "Add Task":
        st.header("➕ Add New Task")
        title = st.text_input("Task Title")
        description = st.text_area("Description")
        category = st.selectbox("Category", ["School", "Personal", "Project", "Other"])
        deadline = st.date_input("Deadline (optional)")
        if st.button("Add Task"):
            add_task(st.session_state.user_id, title, description, category, deadline)
            st.success("Task added successfully!")
            st.experimental_rerun()

    elif menu == "Analytics":
        st.header("📊 Task Analytics")
        tasks = get_tasks(st.session_state.user_id)
        total = len(tasks)
        completed = len([t for t in tasks if t[5]=="Completed"])
        pending = total - completed
        st.metric("Total Tasks", total)
        st.metric("Completed", completed)
        st.metric("Pending", pending)

        # Overall Progress Bar
        overall_progress = (completed / total) if total > 0 else 0
        st.progress(overall_progress)

        # Category-wise Progress
        categories = list(set([t[3] for t in tasks]))
        for cat in categories:
            cat_tasks = [t for t in tasks if t[3]==cat]
            cat_total = len(cat_tasks)
            cat_completed = len([t for t in cat_tasks if t[5]=="Completed"])
            cat_progress = (cat_completed / cat_total) if cat_total > 0 else 0
            st.write(f"**{cat} Progress:**")
            st.progress(cat_progress)

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.success("Logged out successfully!")
        st.experimental_rerun()
