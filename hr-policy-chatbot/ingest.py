#this script is used for reading PDFs, splitting them and storing embeddings in ChromaDB. 
import os 
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_huggingface import HuggingFaceEmbeddings
#Load environment variables from .env file 
load_dotenv()
#Paths 
POLICIES_DIR = '/workspaces/hr-policy-chatbot/hr-policy-chatbot/data/policies'
VECTORSTORE_DIR = '/workspaces/hr-policy-chatbot/hr-policy-chatbot/vectorstore'

def ingest_documents(): 
    print('Step 1: Loading PDF files...')
    #This loader reads ALL PDFs from the folder automatically 
    loader = PyPDFDirectoryLoader(POLICIES_DIR)
    documents = loader.load()
    print(f'Loaded {len(documents)} pagesfrom PDFs.')
    print('Step 2: Splitting into chunks...')
    #chunk_size: max characters per chunk 
    #chunk_overlap : how many chars overlap between chunks 
    #(overlap helps avoid cutting answers mid-sentence) 
    splitter = RecursiveCharacterTextSplitter(chunk_size = 800, chunk_overlap = 150,separators = ['\n\n','\n','.',' ']
    )
    chunks = splitter.split_documents(documents)
    print(f' Created {len(chunks)} chunks.')
    print('Step 3: Creating embeddings and storing in ChromaDB...')
    #Hugging Face embeddings convert the text into vectors 
    embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
    #Chroma.from_documents: creates/updates the vector store 
    vectorstore = Chroma.from_documents(
        documents = chunks, 
        embedding = embeddings, 
        persist_directory = VECTORSTORE_DIR
    )
    print(f'Done! {len(chunks)} chunks stored in ChromaDB')
    return vectorstore
if __name__ == '__main__':
    ingest_documents() 

