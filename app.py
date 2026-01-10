import streamlit as st
import pandas as pd
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. WEB DEV & DESIGN SKILLS: Custom CSS Configuration
# -----------------------------------------------------------------------------
# This block uses HTML/CSS to override the default Streamlit look.
# It makes the app look like a custom product, not just a data script.
st.set_page_config(page_title="TaskEase", page_icon="✅", layout="centered")

custom_css = """
<style>
    /* Main Background adjustments */
    .stApp {
        background-color: #0D1B2A;  /* Dark blue */
        color: #FFFFFF;              /* Make text white by default */
    }
    
    /* Title Styling */
    h1 {
        color: #E0E0E0;              /* Light color for contrast */
        font-family: 'Helvetica', sans-serif;
        font-weight: 700;
    }
    
    /* Custom Card Style for Tasks */
    .task-card {
        background-color: #1B263B;   /* Slightly lighter dark blue for cards */
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 10px;
        color: #FFFFFF;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #1B263B;   /* Dark blue sidebar */
    }
    
    /* Text inside sidebar */
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. PYTHON SKILLS: Backend Logic (Session State)
# -----------------------------------------------------------------------------
# Since we don't have a database, we use 'session_state' to remember tasks 
# as long as the browser tab is open.

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

def add_task():
    task_name = st.session_state.input_task
    task_cat = st.session_state.input_category
    if task_name:
        # Create a dictionary for the task (JSON structure)
        new_task = {
            "name": task_name,
            "category": task_cat,
            "created_at": datetime.now().strftime("%H:%M"),
            "completed": False
        }
        st.session_state.tasks.append(new_task)
        # Clear the text input by resetting the key
        st.session_state.input_task = "" 

def delete_task(index):
    st.session_state.tasks.pop(index)

# -----------------------------------------------------------------------------
# 3. PRODUCT DESIGN: Layout & User Interface
# -----------------------------------------------------------------------------

# --- Sidebar (The "Control Panel") ---
with st.sidebar:
    st.title("⚡ TaskEase")
    st.markdown("### Add a New Task")
    
    # Input forms
    st.text_input("What needs to be done?", key="input_task")
    st.selectbox("Category", ["Work", "Personal", "Learning", "Health"], key="input_category")
    
    # Button triggers the python function 'add_task'
    st.button("Add Task", on_click=add_task, type="primary")
    
    st.markdown("---")
    st.write(f"📊 Total Tasks: **{len(st.session_state.tasks)}**")

# --- Main Area (The "Dashboard") ---
st.title("My Tasks")
st.markdown("Welcome back! Here is your agenda for today.")

# If no tasks exist, show a friendly empty state
if not st.session_state.tasks:
    st.info("No tasks yet. Add one from the sidebar to get started! 🚀")

# Loop through tasks and display them
for i, task in enumerate(st.session_state.tasks):
    # Create columns to layout the task info and the delete button side-by-side
    col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
    
    # Logic to handle the display
    with col1:
        # A simple visual indicator based on category
        icon = "💼" if task['category'] == "Work" else "🏠"
        st.write(f"### {icon}")
        
    with col2:
        # Using HTML here to render the custom 'task-card' style defined in CSS above
        st.markdown(f"""
        <div class="task-card">
            <strong>{task['name']}</strong><br>
            <span style="color:gray; font-size:12px;">{task['category']} • {task['created_at']}</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        # Vertical alignment spacer
        st.write("") 
        st.write("")
        if st.button("Delete", key=f"del_{i}"):
            delete_task(i)
            st.rerun() # Refresh the app immediately