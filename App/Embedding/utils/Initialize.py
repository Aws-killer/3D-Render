from langchain.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.vectorstores import Pinecone
from fastapi import BackgroundTasks
from functools import lru_cache
import os, requests
import pinecone, pprint
from .Elastic import FetchDocuments


index_name = "movie-recommender-fast"
model_name = "thenlper/gte-base"
embeddings = HuggingFaceEmbeddings(model_name=model_name)


TMDB_API = os.environ.get("TMDB_API")

# get api key from app.pinecone.io
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
# find your environment next to the api key in pinecone console
PINECONE_ENV = os.environ.get("PINECONE_ENVIRONMENT")

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
vector_index = pinecone.Index(index_name=index_name)


docsearch = Pinecone.from_existing_index(index_name, embeddings)


def check_if_exists(text, imdb_id):
    results = docsearch.similarity_search(text, filter={"key": {"$eq": imdb_id}}, k=1)
    if results:
        return True
    else:
        return False


def add_document(imdb_id, doc):
    text, temp_doc = doc
    response = check_if_exists(text=text, imdb_id=imdb_id)
    if response:
        print("document exists")
        return

    temp_doc["key"] = imdb_id
    temp_doc["genre_ids"] = ""
    temp = Document(
        page_content=text,
        metadata=temp_doc,
    )
    print("document added")
    docsearch.add_documents([temp])


def generate_text(doc):
    if doc["tv_results"]:
        return pprint.pformat(doc["tv_results"][0]), doc["tv_results"][0]
    return pprint.pformat(doc["movie_results"][0]), doc["movie_results"][0]


def IdSearch(query: str, background_task: BackgroundTasks):
    doc = requests.get(
        f"https://api.themoviedb.org/3/find/{query}?external_source=imdb_id&language=en&api_key={TMDB_API}"
    ).json()
    try:
        text, props = generate_text(doc)
    except Exception as e:
        print(e)
        return []
    background_task.add_task(add_document, imdb_id=query, doc=(text, props))
    return TextSearch(text, filter={"key": {"$ne": query}})


def TextSearch(query: str, filter=None):
    docs = docsearch.similarity_search(query, k=10, filter=filter)
    keys = [doc.metadata["key"] for doc in docs]
    return FetchDocuments(keys)
