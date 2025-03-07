import streamlit as st
from groq import Groq
import time
import streamlit_shadcn_ui as ui
import re


st.title('To-do List')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask anything....")
    #with st.chat_message("user"):
        #st.markdown(prompt)
    #st.session_state.messages.append({"role": "user", "content": prompt})

client = Groq(
    api_key= "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",
)

prompt1 = f"""Provide a detailed, step-by-step approach to solving the following problem:
    {prompt}
    
    Condense the response in 3 oneline steps steps, responce should be short, condensed and don't give me anything else except those 3 oneline step FOLLOW THIS PROMPT AT ALL TIMES"""

if prompt:
    chat = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt1,
            }
        ],
        model="mixtral-8x7b-32768",
    )
try:    
    response = chat.choices[0].message.content
except:
    pass

try:
    with st.chat_message("assistant"):
        #st.markdown(response)
        pattern = r"^\d+\.\s(.*?)(?=\n\d+\.|\Z)"
        points = re.findall(pattern, response, flags=re.MULTILINE)
        #st.markdown(points)
        for i, point in enumerate(points, 1):
            st.checkbox(f"{point}")

    st.session_state.messages.append({"role": "assistant", "content": response})
except:
    pass


