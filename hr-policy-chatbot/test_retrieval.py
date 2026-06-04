from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
load_dotenv()
embeddings = HuggingFaceEmbeddings(model_name = 'all-MiniLM-L6-v2')
db = Chroma(persist_directory= '/workspaces/hr-policy-chatbot/hr-policy-chatbot/vectorstore',embedding_function=embeddings)
results = db.similarity_search_with_score('How many leave days do employees get?',k=3)
for doc, score in results: 
    print(f'Score: {score:.4f}')
    print(f'Content: {doc.page_content[:200]}')
    print(f'Source: {doc.metadata}')
    print('---')