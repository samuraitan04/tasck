# TASCK - Task Management Application

![text](https://github.com/samuraitan04/tasck/blob/main/logo.png?raw=true)

## problem Statement

  Many people struggle with managing large or complex tasks because they can feel overwhelming and difficult to approach. Breaking down these tasks into smaller, actionable steps is often a time-consuming process. The lack of a clear structure can lead to confusion, procrastination, and decreased productivity.  

## Overview

**TASCK** is a task management web application built with Streamlit. It allows users to create tasks, break them down into subtasks, mark tasks and subtasks as completed, edit task details, and remove tasks. The application also integrates with OpenAI's Groq API to generate tasks and subtasks from a natural language description.

## Requirements

To run the application, ensure the following dependencies are installed:
- `groq` (>= 0.18.0)
- `streamlit` (>= 1.43.0)
- `streamlit-elements` (>= 0.1.0)

Use the `requirements.txt` to install dependencies:
```text
groq>=0.18.0
streamlit>=1.43.0
streamlit-elements>=0.1.0
```

## Features

### Task Management
- **Add Tasks**: Tasks can be manually added from a prompt.
- **Subtask Generation**: Generate subtasks automatically using Groq AI by providing a task description.
- **Edit Tasks**: Edit task titles, content, and subtasks.
- **Completion Tracking**: Track completion of tasks and subtasks with checkboxes.
- **Delete Tasks**: Remove tasks and subtasks, or clear all tasks.
- **Remove Completed Tasks**: Option to remove all completed tasks and subtasks.

### User Interface

- **Task List**: Displays the list of tasks on the left-hand side with options to mark them as completed, edit them, or delete them.
- **Task Editor**: The right side of the interface allows editing of the selected task's title, subtasks, and notes.
- **Task Notes**: You can add detailed notes for each task.
- **AI Task Generator**: Use the AI-based Groq API to generate task and subtask suggestions from a prompt.


## How to Run the App

1. Install the dependencies using the following command:
   ```bash
   pip install -r requirements.txt
   ```
   
2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
   
3. Open the app in your browser and start managing your tasks.

---
