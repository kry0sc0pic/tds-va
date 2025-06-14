__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import uvicorn
import os
import shutil
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings 

if 'chroma_langchain_db' not in os.listdir():
    # os.system('unzip chroma_langchain_db.zip')
    print("Unpackign Folder")
    shutil.unpack_archive('./chroma_langchain_db.zip','./','zip')

llm = ChatOpenAI()
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = Chroma(
    collection_name='example_collection',
    embedding_function=embeddings,
    persist_directory='./chroma_langchain_db'
)
retriever = vector_store.as_retriever()

system_prompt = (
    "Use the given context to answer the question. "
    "If you don't know the answer, say you don't know. "
    "Use three sentence maximum and keep the answer concise. "
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, prompt)
chain = create_retrieval_chain(retriever, question_answer_chain)

class LinkData(BaseModel):
    url: str
    text: str

class ResponseData(BaseModel):
    answer: str
    links: list[LinkData]



class RequestData(BaseModel):
    question: str
    image: str | None

app = FastAPI()

@app.post('/api')
async def api(body: RequestData):
    q = body.question
    result = chain.invoke({"input": q})
    links = []
    for c in result['context']:
        link = {
            "text": c.page_content,
            "url": f'https://discourse.onlinedegree.iitm.ac.in'+c.metadata['url']
        }
        links.append(link)
    res = {
        "answer": result['answer'],
        "links": links
    }
    return res


if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0',port=int(os.environ.get('PORT',8080)))