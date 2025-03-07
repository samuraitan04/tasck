import streamlit as st
from groq import Groq
import time
#import streamlit_shadcn_ui as ui
import re


st.title('To-do List')

if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize todos in session state if not already present
if "todos" not in st.session_state:
    st.session_state.todos = []

# Display existing todos
st.subheader("Your To-Do Items")
for i, todo in enumerate(st.session_state.todos):
    # Create a unique key for each checkbox
    checked = st.checkbox(todo["text"], value=todo["done"], key=f"todo_{i}")
    # Update the done status if checkbox state changes
    if checked != todo["done"]:
        st.session_state.todos[i]["done"] = checked
        st.rerun()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask anything....")

client = Groq(
    api_key= "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",
)

if prompt:
    # Add the user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    prompt1 = f"""Provide a detailed, step-by-step approach to solving the following problem:
        {prompt}
        
        Condense the response in 3 oneline steps steps, responce should be short, condensed and don't give me anything else except those 3 oneline step FOLLOW THIS PROMPT AT ALL TIMES"""

    try:    
        chat = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt1,
                }
            ],
            model="mixtral-8x7b-32768",
        )
        response = chat.choices[0].message.content
        
        # Display assistant response in chat
        with st.chat_message("assistant"):
            st.markdown(response)
        
        # Add response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Extract to-do items from response
        pattern = r"^\d+\.\s(.*?)(?=\n\d+\.|\Z)"
        points = re.findall(pattern, response, flags=re.MULTILINE)
        
        # Add new todos from the response
        new_items_added = False
        for point in points:
            # Only add if it's not already in the list
            if not any(todo["text"] == point for todo in st.session_state.todos):
                st.session_state.todos.append({"text": point, "done": False})
                new_items_added = True
        
        # Display confirmation, clear chat history, and rerun to show new items
        if new_items_added:
            # Clear the chat history
            st.session_state.messages = []
            st.success("Added new to-do items!")
            st.rerun()
            
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Add a button to clear all to-do items
if st.button("Clear All To-Do Items"):
    st.session_state.todos = []
    st.session_state.messages = []
    st.success("All to-do items cleared!")
    st.rerun()


