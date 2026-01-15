import streamlit as st
import json
from datetime import datetime
import os

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="TaskEase", page_icon="✅", layout="centered")

# ---------------------- CUSTOM CSS ----------------------
custom_css = """
<style>
.stApp { background-color: #0D1B2A; color: #FFFFFF; }
h1 { color: #E0E0E0; font-family: 'Helvetica', sans-serif; font-weight: 700; }

.task-card {
    background-color: #1B263B;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #4CAF50;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    margin-bottom: 10px;
    color: #FFFFFF;
}
.task-completed {
    background-color: #1B263B;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #FF4B4B;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    margin-bottom: 10px;
    color: gray;
    text-decoration: line-through;
}
section[data-testid="stSidebar"] { background-color: #1B263B; }
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] label { color: #FFFFFF !important; }
div.stButton > button { width: 100%; margin-top: 5px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------- FILE PERSISTENCE ----------------------
DATA_FILE = "tasks.json"

# Load tasks from file if exists
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        st.session_state.tasks = json.load(f)
else:
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []

# ---------------------- HELPER FUNCTIONS ----------------------
def save_tasks():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.tasks, f)

def add_task():
    task_name = st.session_state.input_task
    task_cat = st.session_state.input_category
    if task_name:
        new_task = {
            "name": task_name,
            "category": task_cat,
            "created_at": datetime.now().strftime("%H:%M"),
            "completed": False
        }
        st.session_state.tasks.append(new_task)
        st.session_state.input_task = ""
        save_tasks()

def delete_task(index):
    st.session_state.tasks.pop(index)
    save_tasks()

def toggle_complete(index):
    st.session_state.tasks[index]['completed'] = not st.session_state.tasks[index]['completed']
    save_tasks()

def edit_task(index):
    new_name = st.session_state[f"edit_{index}"]
    st.session_state.tasks[index]['name'] = new_name
    save_tasks()

# ---------------------- SIDEBAR ----------------------
with st.sidebar:
    st.title("⚡ TaskEase")
    st.markdown("### Add a New Task")
    
    st.text_input("What needs to be done?", key="input_task")
    st.selectbox("Category", ["Work", "Personal", "Learning", "Health"], key="input_category")
    
    st.button("Add Task", on_click=add_task, type="primary")
    
    st.markdown("---")
    st.write(f"📊 Total Tasks: **{len(st.session_state.tasks)}**")

# ---------------------- MAIN DASHBOARD ----------------------
st.title("My Tasks")
st.markdown("Welcome back! Here is your agenda for today.")

if not st.session_state.tasks:
    st.info("No tasks yet. Add one from the sidebar to get started! 🚀")

# Category icons
icons = {"Work":"💼", "Personal":"🏠", "Learning":"📚", "Health":"🏋️"}

# Display tasks
for i, task in enumerate(st.session_state.tasks):
    col1, col2, col3 = st.columns([0.1, 0.7, 0.2])
    
    with col1:
        icon = icons.get(task['category'], "📝")
        st.write(f"### {icon}")
    
    with col2:
        card_class = "task-completed" if task['completed'] else "task-card"
        st.markdown(f"""
        <div class="{card_class}">
            <strong>{task['name']}</strong><br>
            <span style="color:gray; font-size:12px;">{task['category']} • {task['created_at']}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Edit task input
        st.text_input("Edit task", value=task['name'], key=f"edit_{i}")
        if st.button("Save", key=f"save_{i}"):
            edit_task(i)
            st.rerun()
    
    with col3:
        st.button("⭕", key=f"complete_{i}", help="Mark complete", on_click=toggle_complete, args=(i,))
        st.button("🗑️", key=f"del_{i}", help="Delete task", on_click=delete_task, args=(i,))
