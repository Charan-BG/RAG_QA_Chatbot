import streamlit as st
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os

from dotenv import load_dotenv
load_dotenv()

## Set up Streamlit
st.title("RAG-based Conversational Chatbot")
st.write("Upload PDFs and chat with their content")

## Input the Groq API Key and Hugging Face API Key
groq_api_key = st.text_input("Enter your Groq API key:", type="password")
hf_api_key = st.text_input("Enter your Hugging Face API key:", type="password")

## Check if both API keys are provided
if groq_api_key and hf_api_key:
    os.environ['HF_TOKEN'] = hf_api_key
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    llm = ChatGroq(groq_api_key=groq_api_key, model_name="Gemma2-9b-It")

    ## Chat interface
    session_id = st.text_input("Session ID", value="default_session")

    ## Statefully manage chat history
    if 'store' not in st.session_state:
        st.session_state.store = {}

    uploaded_files = st.file_uploader("Choose a PDF file", type="pdf", accept_multiple_files=True)

    ## Process uploaded PDFs
    if uploaded_files:
        documents = []
        for uploaded_file in uploaded_files:
            temppdf = f"./temp.pdf"
            with open(temppdf, "wb") as file:
                file.write(uploaded_file.getvalue())
                file_name = uploaded_file.name

            loader = PyPDFLoader(temppdf)
            docs = loader.load()
            documents.extend(docs)

        # Split and create embeddings for the documents
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
        splits = text_splitter.split_documents(documents)

        vectorstore = FAISS.from_documents(documents, embeddings)

        retriever = vectorstore.as_retriever()

        contextualize_q_system_prompt = ("""
            Note: this is very important and high priority, If the human prompt is looking for an answer which is out of 
            context given, clearly state that "you don't know and tell it's out of context".
            You are provided with a chat history and the latest user question, 
            which may refer to previous messages. Your task is to rewrite the 
            latest user question into a standalone question that does not rely 
            on prior context for understanding. Ensure the reformulated question 
            is clear and concise. If no rephrasing is needed, return the question 
            unchanged. Do not provide an answer.
        """)

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

        # Answer question
        system_prompt = """
            You are an assistant specialized in answering questions. 
            Utilize the provided retrieved context to formulate your response. 
            Note: this is very important and high priority, If the human prompt is looking for an answer which is out of 
            context given, clearly state that "you don't know and tell it's out of context".

            {context}
        """

        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        def get_session_history(session: str) -> BaseChatMessageHistory:
            if session_id not in st.session_state.store:
                st.session_state.store[session_id] = ChatMessageHistory()
            return st.session_state.store[session_id]

        conversational_rag_chain = RunnableWithMessageHistory(
            rag_chain, get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer"
        )

        user_input = st.text_input("Your question:")
        if user_input:
            session_history = get_session_history(session_id)
            response = conversational_rag_chain.invoke(
                {"input": user_input},
                config={
                    "configurable": {"session_id": session_id}
                },
            )
            st.write(st.session_state.store)
            st.write("Assistant:", response['answer'])
            st.write("Chat History:", session_history.messages)
else:
    st.warning("Please enter both the Groq API Key and Hugging Face API Key.")
