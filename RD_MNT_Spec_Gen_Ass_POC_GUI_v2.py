import streamlit as st
from openai import OpenAI
import os
import time


# 建立 message、run 對話函式
def input_and_run(input, thread_id, assistant_id):
    message = client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=input
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return message, run


# 判斷 Model 是否執行完成
def wait_on_run(run):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run


# LLM - Set OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API"))

# LLM - Set assistant id
assistant_id = "asst_4q4t10Ia0qoPkY45TsGjJAmi"

# LLM - Set thread id
if "clicked" not in st.session_state:
    st.session_state.clicked = "thread_uQ3HSBfIa6IgJdOGJWYm35Hr"

# ST - Side_Bar
# st_btn => create new thread and clean chat window
btn_chat = st.sidebar.button("New Chat", type="secondary")

if btn_chat:
    # Create thread
    thread = client.beta.threads.create()
    st.session_state.clicked = thread.id
    # Clean chat window
    st.session_state.messages = []
    # show status
    st.sidebar.write("新對話窗，出來囉!!!")

# st_uploader => select files
uploaded_files = st.sidebar.file_uploader(
    "Upload files", accept_multiple_files=True, label_visibility="hidden"
)

# st_btn => submit file to cloud
button_ans = st.sidebar.button("Confirm", type="primary")
ids = []
if button_ans:
    if len(uploaded_files) > 0:
        for upload_file in uploaded_files:
            file = client.files.create(file=upload_file, purpose="assistants")
            ids.append(file.id)
            st.sidebar.write(f"{upload_file.name} => ids: {file.id}")

        # import files to Message to thread
        message = client.beta.threads.messages.create(
            thread_id=st.session_state.clicked,
            role="user",
            content="我將下指令，請你協助我處理這些文檔。",
            file_ids=ids,
        )
        message_id = message.id

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.clicked, assistant_id=assistant_id
        )

        run = wait_on_run(run)

        st.sidebar.write("執行完啦!!")
        # # Update GPT-Assistant (import files to assistant)
        # ssistant_file = client.beta.assistants.update(
        #     assistant_id=assistant_id,
        #     tools=[{"type": "retrieval"}],
        #     file_ids=ids,  # 添加文件清單
        # )
    else:
        st.sidebar.write("there are no files to upload.")

export_btn = st.sidebar.button("Export", type="primary")
if export_btn:
    st.sidebar.write("這是資料導出功能")

# show assistand、thread id
st.sidebar.write(f"助理的編號-{assistant_id}")
st.sidebar.write(f"對話串的編號-{st.session_state.clicked}")


# Main_Window
# Chat with LLM
st.title("Chat with Your Adorable Assistant")


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("請輸入問題"):

    # Add user message to chat history (streamlit)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message, run = input_and_run(prompt, st.session_state.clicked, assistant_id)
        message_id = message.id
        run = wait_on_run(run)
        msgs = client.beta.threads.messages.list(
            thread_id=st.session_state.clicked, order="asc", after=message_id
        )
        st.markdown(msgs.data[0].content[0].text.value)
        response = msgs.data[0].content[0].text.value

    # Add assistant message in chat message (streamlit)
    st.session_state.messages.append({"role": "assistant", "content": response})
