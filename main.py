import streamlit as st
from groq import Groq
import time
import re
import json
from streamlit_elements import elements, dashboard, mui, html, editor
import base64

def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

st.set_page_config(layout="wide", page_title="TASCK")

background_image_url = "https://media1.giphy.com/media/L2HuVpmuQhK3nu2vfz/giphy.webp?cid=ecf05e47rswuxbqubf8tjsxos6j4rpibg6c29g1h9ivwbu7d&ep=v1_gifs_search&rid=giphy.webp&ct=g"

st.markdown(f"""
<style>
    .stApp {{
        position: relative;
        height: 100%;
        overflow-y: auto;
    }}
    
    body {{
        background: transparent;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }}
    
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        pointer-events: none;
    }}
    
    .main-title {{
        color: #ffffff;
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
    }}
    
    .subheader {{
        color: #ffffff;
        font-size: 1.5em;
        font-weight: 600;
        margin-bottom: 1em;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        position: relative;
    }}
    
    .task-container {{
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        position: relative;
        margin-bottom: 20px;
    }}
    
    .placeholder-text {{
        color: #666;
        font-style: italic;
    }}
    
    .task-container .stMarkdown {{
        color: #000000;
    }}
    
    .stCheckbox {{
        background: transparent !important;
    }}
    
    .stCheckbox > label {{
        background: transparent !important;
        padding: 0 !important;
    }}
    
    .stCheckbox > label > div {{
        background: transparent !important;
        border-radius: 4px;
    }}
    
    .stCheckbox > label > div[data-baseweb="checkbox"] {{
        background: transparent !important;
    }}
    
    .stCheckbox > label > div > div {{
        transform: scale(0.8);
        background: transparent !important;
    }}
    
    div[style*='margin-left: 20px'] .stCheckbox {{
        background: transparent !important;
        margin-right: 5px;
    }}
    
    .stApp > * {{
        position: relative;
        z-index: 1;
    }}

    ::-webkit-scrollbar {{
        width: 10px;
        background: rgba(255, 255, 255, 0.1);
    }}

    ::-webkit-scrollbar-thumb {{
        background: rgba(255, 255, 255, 0.5);
        border-radius: 5px;
    }}

    ::-webkit-scrollbar-track {{
        background: rgba(0, 0, 0, 0.1);
    }}

    .main {{
        overflow-y: auto;
        height: 100vh;
        padding-bottom: 50px;
    }}

    .element-container {{
        overflow: visible !important;
    }}
</style>
""", unsafe_allow_html=True)

st.title('TASCK')

if "messages" not in st.session_state:
    st.session_state.messages = []

if "todos" not in st.session_state:
    st.session_state.todos = []

if "selected_task" not in st.session_state:
    st.session_state.selected_task = None

if "task_content" not in st.session_state:
    st.session_state.task_content = {}

def select_task(task_index):
    st.session_state.selected_task = task_index
    
def save_task_content(task_index, content):
    if task_index is not None and 0 <= task_index < len(st.session_state.todos):
        st.session_state.todos[task_index]["content"] = content
        st.session_state.task_content[task_index] = content

def edit_task_text(task_index, new_text):
    if task_index is not None and 0 <= task_index < len(st.session_state.todos):
        st.session_state.todos[task_index]["text"] = new_text

def update_subtasks_completion(task_index, completed):
    if task_index is not None and 0 <= task_index < len(st.session_state.todos):
        todo = st.session_state.todos[task_index]
        if "subtasks" in todo:
            for subtask in todo["subtasks"]:
                subtask["done"] = completed

def generate_subtasks(task_description):
    client = Groq(api_key="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")
    
    prompt = f"""Break down the following task into 3 smaller subtasks:
        Task: {task_description}
        
        Provide exactly 3 short, actionable subtasks. Each subtask should be one line and start with a dash (-). Don't add any other text."""
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
        )
        response = chat.choices[0].message.content
        subtasks = [line.strip()[2:].strip() for line in response.split('\n') if line.strip().startswith('-')]
        return subtasks
    except Exception as e:
        st.error(f"Error generating subtasks: {e}")
        return []

def check_subtasks_completion(task):
    if not task.get("subtasks"):
        return task.get("done", False)
    return all(subtask.get("done", False) for subtask in task.get("subtasks", []))

def update_task_completion(task_index):
    if task_index is not None and 0 <= task_index < len(st.session_state.todos):
        todo = st.session_state.todos[task_index]
        if todo.get("subtasks"):
            todo["done"] = check_subtasks_completion(todo)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Your Tasks")
    
    for i, todo in enumerate(st.session_state.todos):
        col_check, col_text, col_edit = st.columns([0.1, 0.7, 0.2])
        
        with col_check:
            checked = st.checkbox("", value=todo.get("done", False), key=f"todo_{i}")
            if checked != todo.get("done", False):
                st.session_state.todos[i]["done"] = checked
                update_subtasks_completion(i, checked)
                st.rerun()
        
        with col_text:
            if todo.get("done", False):
                st.markdown(f"<span style='text-decoration: line-through; color: #666;'>{todo['text']}</span>", unsafe_allow_html=True)
            else:
                st.markdown(todo['text'])
            
            if todo.get("subtasks"):
                for j, subtask in enumerate(todo["subtasks"]):
                    subtask_text = subtask['text']
                    if subtask.get('done', False) or todo.get('done', False):
                        subtask_display = f"<span style='text-decoration: line-through; color: #666;'>{subtask_text}</span>"
                    else:
                        subtask_display = subtask_text
                    
                    st.markdown(
                        f"""<div style='margin-left: 20px; display: flex; align-items: center;'>""",
                        unsafe_allow_html=True
                    )
                    sub_checked = st.checkbox(
                        "", 
                        value=subtask.get("done", False) or todo.get("done", False),
                        key=f"subtask_{i}_{j}",
                        disabled=todo.get("done", False)
                    )
                    st.markdown(f"&nbsp;{subtask_display}", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    if sub_checked != subtask.get("done", False):
                        todo["subtasks"][j]["done"] = sub_checked
                        update_task_completion(i)
                        st.rerun()
        
        with col_edit:
            if st.button("Edit", key=f"edit_{i}"):
                select_task(i)
                st.rerun()
    
    if st.button("Clear All Tasks"):
        st.session_state.todos = []
        st.session_state.messages = []
        st.session_state.task_content = {}
        st.session_state.selected_task = None
        st.success("All tasks cleared!")
        st.rerun()
    
    if st.button("Remove Completed Tasks"):
        # First, remove completed subtasks from remaining tasks
        for todo in st.session_state.todos:
            if todo.get("subtasks"):
                todo["subtasks"] = [subtask for subtask in todo["subtasks"] if not subtask.get("done", False)]
        
        # Then remove completed main tasks
        st.session_state.todos = [todo for todo in st.session_state.todos if not todo.get("done", False)]
        st.success("Completed tasks and subtasks removed!")
        st.rerun()

with col2:
    if st.session_state.selected_task is not None and 0 <= st.session_state.selected_task < len(st.session_state.todos):
        st.subheader("Edit Task")
        selected_todo = st.session_state.todos[st.session_state.selected_task]
        
        new_task_text = st.text_input("Task Title", value=selected_todo['text'], key="task_title_editor")
        if new_task_text != selected_todo['text']:
            edit_task_text(st.session_state.selected_task, new_task_text)
        
        st.subheader("Subtasks")
        
        if "subtasks" not in selected_todo:
            selected_todo["subtasks"] = []
        
        for i, subtask in enumerate(selected_todo["subtasks"]):
            col_check, col_text, col_delete = st.columns([0.1, 0.7, 0.2])
            
            with col_check:
                checked = st.checkbox("", 
                                   value=subtask.get("done", False) or selected_todo.get("done", False), 
                                   key=f"subtask_{i}", 
                                   disabled=False)
                if checked != subtask.get("done", False):
                    selected_todo["subtasks"][i]["done"] = checked
                    update_task_completion(st.session_state.selected_task)
                    st.rerun()
            
            with col_text:
                if subtask.get("done", False) or selected_todo.get("done", False):
                    st.markdown(f"<span style='text-decoration: line-through; color: #666;'>{subtask['text']}</span>", unsafe_allow_html=True)
                else:
                    subtask_text = st.text_input("", value=subtask["text"], key=f"subtask_text_{i}")
                    if subtask_text != subtask["text"]:
                        selected_todo["subtasks"][i]["text"] = subtask_text
            
            with col_delete:
                if st.button("🗑", key=f"delete_subtask_{i}"):
                    selected_todo["subtasks"].pop(i)
                    update_task_completion(st.session_state.selected_task)
                    st.rerun()
        
        if not selected_todo.get("done", False):
            new_subtask = st.text_input("Add Subtask", key="new_subtask")
            col1_sub, col2_sub = st.columns(2)
            
            with col1_sub:
                if st.button("Add Subtask"):
                    if new_subtask:
                        selected_todo["subtasks"].append({"text": new_subtask, "done": False})
                        update_task_completion(st.session_state.selected_task)
                        st.rerun()
            
            with col2_sub:
                if st.button("Generate Subtasks from This"):
                    if new_subtask:
                        new_subtasks = generate_subtasks(new_subtask)
                        for subtask in new_subtasks:
                            if not any(existing["text"] == subtask for existing in selected_todo["subtasks"]):
                                selected_todo["subtasks"].append({"text": subtask, "done": False})
                        update_task_completion(st.session_state.selected_task)
                        st.success("Generated new subtasks!")
                        st.rerun()
                    else:
                        st.warning("Please enter a task description first!")
            
            if st.button("Generate Subtasks from Main Task"):
                new_subtasks = generate_subtasks(selected_todo["text"])
                for subtask in new_subtasks:
                    if not any(existing["text"] == subtask for existing in selected_todo["subtasks"]):
                        selected_todo["subtasks"].append({"text": subtask, "done": False})
                update_task_completion(st.session_state.selected_task)
                st.success("Generated new subtasks!")
                st.rerun()

        st.subheader("Task Notes")
        task_content = st.text_area(
            "Task Notes",
            value=selected_todo.get("content", ""),
            height=300,
            key="task_content_editor"
        )
        
        if task_content != selected_todo.get("content", ""):
            save_task_content(st.session_state.selected_task, task_content)
        
        col_save, col_delete = st.columns(2)
        with col_save:
            if st.button("Save and Close", use_container_width=True):
                st.session_state.selected_task = None
                st.success("Task details saved!")
                st.rerun()
        
        with col_delete:
            if st.button("Delete Task", use_container_width=True):
                if 0 <= st.session_state.selected_task < len(st.session_state.todos):
                    del st.session_state.todos[st.session_state.selected_task]
                    st.session_state.selected_task = None
                    st.success("Task deleted!")
                    st.rerun()
    
    else:
        st.subheader("AI Task Generator")
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        prompt = st.chat_input("Describe your task or project...")
        
        client = Groq(api_key="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")
        
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            prompt1 = f"""Provide a detailed, step-by-step approach to solving the following problem:
                {prompt}
                
                Condense the response in 3 oneline steps steps, responce should be short, condensed and don't give me anything else except those 3 oneline step FOLLOW THIS PROMPT AT ALL TIMES"""
        
            try:    
                chat = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt1}],
                    model="mixtral-8x7b-32768",
                )
                response = chat.choices[0].message.content
                
                with st.chat_message("assistant"):
                    st.markdown(response)
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                pattern = r"^\d+\.\s(.*?)(?=\n\d+\.|\Z)"
                points = re.findall(pattern, response, flags=re.MULTILINE)
                
                new_items_added = False
                for point in points:
                    if not any(todo["text"] == point for todo in st.session_state.todos):
                        st.session_state.todos.append({
                            "text": point, 
                            "done": False,
                            "content": "",
                            "subtasks": []
                        })
                        new_items_added = True
                
                if new_items_added:
                    st.session_state.messages = []
                    st.success("Added new tasks!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
        
        st.subheader("Task Details")
        st.info("Select a task to edit its details.")