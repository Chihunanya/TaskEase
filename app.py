import streamlit as st

st.set_page_config(page_title="TaskEase", layout="wide")

# -------------------------------
# INITIALIZE SESSION STATE
# -------------------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
st.sidebar.title("TaskEase")

page = st.sidebar.radio(
    "Navigate",
    ["Home", "Add Task", "Completed Tasks"]
)

# -------------------------------
# HOME PAGE
# -------------------------------
if page == "Home":
    st.title("TaskEase")
    st.write("Stay organized and productive.")

    pending_tasks = [
        task for task in st.session_state.tasks if not task["completed"]
    ]

    if not pending_tasks:
        st.info("No pending tasks. Add a task to get started!")
    else:
        for index, task in enumerate(pending_tasks):
            col1, col2 = st.columns([0.1, 0.9])

            with col1:
                checked = st.checkbox(
                    "",
                    key=f"home_checkbox_{index}"
                )

            with col2:
                st.write(task["title"])

            if checked:
                task["completed"] = True
                st.rerun()

# -------------------------------
# ADD TASK PAGE
# -------------------------------
elif page == "Add Task":
    st.title("Add a New Task")

    title = st.text_input("Task Title")
    description = st.text_area("Task Description")
    due_date = st.date_input("Due Date")

    if st.button("Save Task"):
        if title.strip() == "":
            st.warning("Task title cannot be empty.")
        else:
            st.session_state.tasks.append({
                "title": title,
                "description": description,
                "due_date": due_date,
                "completed": False
            })
            st.success("Task added successfully!")

# -------------------------------
# COMPLETED TASKS PAGE
# -------------------------------
elif page == "Completed Tasks":
    st.title("Completed Tasks")

    completed_tasks = [
        task for task in st.session_state.tasks if task["completed"]
    ]

    if not completed_tasks:
        st.info("No completed tasks yet.")
    else:
        for task in completed_tasks:
            st.write(f"✔️ {task['title']}")
