__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import json
import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings 
from langchain_core.documents import Document

files = os.listdir('discourse_json')

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
)

docs = []

for (i,file) in enumerate(files):
    print(f"FILE [{i+1}/{len(files)}]")
    with open(f'discourse_json/{file}') as f:
        data = json.load(f)
    posts = data['post_stream']['posts']
    for (j,post) in enumerate( posts):
        print(f"POST [{j+1}/{len(posts)}]")
        doc = Document(
            page_content=post['cooked'],
            metadata={
                "url": post['post_url']
            }
        )
        vector_store.add_documents([doc,])

