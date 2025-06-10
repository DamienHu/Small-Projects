## Step-by-step process for handling PDF files and performing similarity search using embeddings.
#
# 1. Index PDF Files
# 2. Extract Text from PDF Files and Split into Small Chunks
# 3. Send the Chunks to the Embedding Model
# 4. Save the Embeddings to a Vector Database
# 5. Perform Similarity Search on the Vector Database to Find Similar Documents
# 6. Retrieve and Present Similar Documents to the User

## Run `pip install -r requirements.txt` to Install Required Packages.

from langchain.document_loaders import PyPDFLoader

doc_path = "./data/Hardening Windows 11.pdf"
loader = PyPDFLoader(doc_path)
data = loader.load()
print("Done loading PDF...")

content = data[0].page_content
# print(content) # Uncomment to print extracted content for debugging.

## Step: Extract Text from PDF Files and Split into Small Chunks

from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# Initialize text splitter to chunk the extracted content.
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
chunks = text_splitter.split_documents(data)

print("Done splitting PDF into chunks...")

## Step: Add Vector Database for Storing Embeddings

import ollama
ollama.pull("nomic-embed-text")  # Ensure the embedding model is available.

vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=OllamaEmbeddings(model="nomic-embed-text"),
    collection_name="simple-rag",
)

print("Done adding chunks to vector database...")

## Step: Setup Retrieval and Similarity Search

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnablePassthrough
from langchain.retrievers.multi_query import MultiQueryRetriever

# Set up the language model for generating embeddings.
model = 'llama3.2'
llm = ChatOllama(model=model)

## Define a prompt template to generate multiple versions of a user's question.

QUERY_PROMPT = PromptTemplate(
    input_variables=["question"],
    template="""
        You are an AI language model assistant. Your task is to generate different versions of the given user question
        to retrieve relevant documents from a vector database. By generating multiple perspectives on the user's question,
        your goal is to help overcome some limitations of distance-based similarity search.
        Provide these alternative questions separated by newlines.

        Original Question: {question}
    """
)

# Initialize retriever with multi-query capabilities using embedding model and query prompt template.
retriever = MultiQueryRetriever.from_llm(vector_db.as_retriever(), llm, prompt=QUERY_PROMPT)

## Step: Define the RAG (Retrieval-Augmented Generation) Prompt for Query Answering

template = """Answer the question based ONLY on the following Context:
    {context}
    Question: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# Example user question to demonstrate the retrieval process.
user_question = chain.invoke("Which part of the document offers the most in security?")
print(f"User Question: {user_question}")

## Step: Perform and Display Retrieval

res = chain.invoke({"question": user_question})
print(res)