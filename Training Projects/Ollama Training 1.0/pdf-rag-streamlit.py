from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever
import streamlit as st
import logging
import os
import ollama
import sys

logging.basicConfig(
    level=logging.INFO,  # Show INFO and above
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Print logs to stdout (console)
    ]
)

#Constants
DOC_PATH = "./data/Hardening Windows 11.pdf"
MODEL_NAME = "llama3.2"
EMBEDDING_MODEL = "nomic-embed-text"
VECTOR_STORE_NAME = "simple-rag"
PERSIST_DIRECTORY = "./chroma_db"

def ingest_pdf(doc_path):
    """Load PDF documents."""
    if os.path.exists(doc_path):
        loader = PyPDFLoader(file_path=doc_path)
        data= loader.load()
        logging.info("PDF loaded succeessfully.")
        return data
    else:
        logging.error(f"PDF file not found at path: {doc_path}")
        return None

def split_documents(documents):
    """Split documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size =1200,chunk_overlap =300)
    chunks = text_splitter.split_documents(documents)
    logging.info("Documents split into chunks.")
    return chunks

@st.cache_resource
def load_vector_db():
    """Load or create the vector database"""
    #Pull the embedding model if not already available
    ollama.pull(EMBEDDING_MODEL)

    embedding = OllamaEmbeddings(model = EMBEDDING_MODEL)

    if os.path.exists(PERSIST_DIRECTORY):
        vector_db = Chroma(
            embedding_function=embedding,
            collection_name=VECTOR_STORE_NAME,
            persist_directory=PERSIST_DIRECTORY,
        )
        logging.info("Loaded existing vector database.")
    else:
        #Load and proces the PDF document
        data = ingest_pdf(DOC_PATH)
        if data is None:
            return None
        
        #Split the documents into chunks
        chunks = split_documents(data)

        vector_db = Chroma.from_documents(
            documents=chunks,
            embedding=embedding,
            collection_name=VECTOR_STORE_NAME,
            persist_directory=PERSIST_DIRECTORY,
        )
        vector_db.persist()
        logging.info("Vecotr database created and persisted.")
    return vector_db

def create_vector_db(chunks):
    """Create a vector database from document chunks."""
    #Pull the embedding model if not already available
    ollama.pull(EMBEDDING_MODEL)

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=OllamaEmbeddings(model=EMBEDDING_MODEL),
        collection_name=VECTOR_STORE_NAME
    )
    logging.info("Vector database created.")
    return vector_db

def create_retriever(vector_db,llm):
    """Create a multi-query retriever"""
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""
        You are an AI language model assistant. Your task is to generate different versions of the given user question to retrieve 
        relevant documents from a vector database. By generating mutliple perspectives on the user's question, 
        your goal is to help the user overcome some of the limitations of distance-based similarity search. Provide these alternative questions separated
        by newlines.
        Original Question: {question}
        """
    )
    retriever = MultiQueryRetriever.from_llm(vector_db.as_retriever(),llm,prompt = QUERY_PROMPT)

    logging.info("Retriever created.")
    return retriever

def create_chain(retriever, llm):
    """Create the chain"""
    #RAG prompt
    template = """Answer the question based ONLY on the following Context:
        {context}
        Question: {question}
        """
    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        |StrOutputParser()
    )
    logging.info("Chain created successfully.")
    return chain

def main():
    st.title("Document Assistant")

    #User input
    user_input = st.text_input("Enter your question:")

    if user_input:
        with st.spinner("Generating response...."):
            try:
                #Init LLM
                llm = ChatOllama(model=MODEL_NAME)

                #Create the vector database
                vector_db = load_vector_db()

                #Initialize the language model
                llm = ChatOllama(model=MODEL_NAME)

                #Create the retriever
                retriever = create_retriever(vector_db,llm)

                #Create the chain with preserved syntax
                chain = create_chain(retriever, llm)

                #Example query
                question = "Top ways to Harden my system?"

                #Get the response
                res = chain.invoke(question)

                st.markdown("**Assistant:**")
                st.write(res)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.info("Please enter a question to get started.")

if __name__ == "__main__":
    main()