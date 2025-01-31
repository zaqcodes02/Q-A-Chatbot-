from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pinecone
from langchain.chains import RetrievalQA
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load API keys
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8001"],  # Allow requests from your frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Pydantic model to receive the query
class QueryRequest(BaseModel):
    query: str

# Initialize Pinecone
pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)

# Pinecone index setup
index_name = "bookembeddings"
index = pc.Index(index_name)

# Initialize embeddings model
embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Initialize Pinecone vector store
vector_store = PineconeVectorStore(index=index, embedding=embeddings_model)

# Initialize Groq LLM
LLM = ChatGroq(model_name="llama-3.1-8b-instant", api_key=GROQ_API_KEY)

# Create a RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=LLM,
    chain_type="stuff",
    retriever=vector_store.as_retriever(),
    return_source_documents=True
)

# Function to query the bot
def query_bot(query: str):
    query_with_instruction = f"{query} Please provide a concise response in 2 to 3 sentences."
    result = qa_chain({"query": query_with_instruction})
    answer = result.get("result", "")
    sources = result.get("source_documents", [])

    # If no sources are found, return "No context found"
    if not sources:
        answer = "No context found"
    
    return answer

# FastAPI endpoint to process queries
@app.post("/query")
async def query_endpoint(request: QueryRequest):
    try:
        query = request.query
        # Call the query_bot function to get the answer and source documents
        answer = query_bot(query)
        
        # Return the response in the desired format
        return {
            "answer": answer,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)