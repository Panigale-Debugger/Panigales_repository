import os 
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate 
from confidence import compute_confidence 

load_dotenv()
VECTORSTORE_DIR = '/workspaces/hr-policy-chatbot/hr-policy-chatbot/vectorstore' 
TOP_K = 4
SYSTEM_PROMPT = """
You are a helpful HR policy Assistant for a company. 
Your job is to answer employee quesitons based ONLY on the 
HR policy documents provided by to you as contex. 

Rules you must follow: 
1. only use information from the provided content 
2. If the context does not contain the answer, say: 
'I could not find specific information about this in the HR policies.' 
3. Be concise and professional. 
4. Always mention the relevant policy section if available. 
5. Never guess or make up policy details. 
"""
USER_PROMPT = """
Context from HR policy Documents: 
---
{context}
---
Employe Question: {question}
Please provide a clear, helpful answer based on the context above. 
"""
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name = 'all-MiniLM-L6-v2')
    return Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings
    )
def ask_question(question: str, vectorstore) -> dict: 
    results = vectorstore.similarity_search_with_score(question, k=TOP_K)
    if not results: 
        return {
            'answer':'no relevant policy information found.',
            'confidence': 0,
            'sources':[],
            'scores': []
        }
    docs = [doc for doc, _ in results]
    scores = [score for _, score in results]
    confidence = compute_confidence(scores)
    context_parts = []
    for i, doc in enumerate(docs):
        source = doc.metadata.get('source','Unknown')
        page = doc.metadata.get('page',0)
        context_parts.append(
            f'[Source {i+1} : {os.path.basename(source)},'
            f' Page {page+1}]\n{doc.page_content}'
        )
    context = '\n\n'.join(context_parts)
    llm = ChatGroq(
        model='llama-3.3-70b-versatile',
        api_key=os.getenv('GROQ_API_KEY'),
        temperature=0
    )

    prompt = ChatPromptTemplate.from_messages([
        ('system', SYSTEM_PROMPT),
        ('human', USER_PROMPT)
    ])

    chain = prompt | llm
    response = chain.invoke({'context': context, 'question': question})

    sources = list(set([
        f"{os.path.basename(doc.metadata.get('source', 'Unknown'))}, "
        f"Page {doc.metadata.get('page', 0)+1}"
        for doc in docs
    ]))

    return {
        'answer': response.content,
        'confidence': confidence,
        'sources': sources,
        'scores': scores
    }
