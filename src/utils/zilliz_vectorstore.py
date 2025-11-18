
from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, connections

import os
from pymilvus import Index
from langchain_text_splitters import RecursiveCharacterTextSplitter

from azure_client import connect_azure_embedding
from pathlib import Path
import yaml
import asyncio
from langchain_community.vectorstores import Zilliz

CONFIG_PATH = Path(__file__).parent.parent.parent  / 'config' / 'zilliz_config.yaml'

def load_zilliz_config():
    with CONFIG_PATH.open('r') as f:
        return yaml.safe_load(f)
zilliz_config = load_zilliz_config()

###################################

COLLECTION_NAME = "research_docs"
EMBED_DIM = 1536  

ZILLIZ_CLOUD_URI = zilliz_config["Zilliz_endpoint"]
ZILLIZ_CLOUD_TOKEN = zilliz_config["Zilliz_Token"]  

class ZillizVectorStore:
    def __init__(self):
        # Connect to Zilliz Cloud using API token auth
        connections.connect(
            alias="default",
            uri=ZILLIZ_CLOUD_URI,
            token=ZILLIZ_CLOUD_TOKEN,
            secure=True,
        )
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBED_DIM),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2048),  
        ]
        schema = CollectionSchema(fields=fields, description="Research documents")
        # Create or load the collection
        self.collection = Collection(
            name=COLLECTION_NAME,
            schema=schema,
            using="default"
        )


    def insert_documents(self, embeddings, texts):
        data = [embeddings, texts]
        self.collection.insert(data)
        self.collection.flush()

    def search(self, query_embedding, top_k=5):
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = self.collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["text"]
        )
        hits = results[0] if results else []
        return [hit.entity.get("text") for hit in hits]


    def create_index(self):
        index_params = {
            "index_type": "IVF_FLAT",  # or HNSW, depending on what you prefer
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)

    def load_collection(self):
        self.collection.load()



async def store_in_vector_store(input):
    try:
        azure_embedding = connect_azure_embedding()
        embeddings = azure_embedding['model'] if azure_embedding['status'] else None
        if embeddings is None:
            raise Exception("Failed to connect to Azure Embedding model.")
        # Initialize RecursiveCharacterTextSplitter with desired chunk size and overlap
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(input)

        # Run blocking vector store operations in thread to avoid blocking event loop
        def blocking_store():
            vector_store = ZillizVectorStore()
            doc_embeddings = embeddings.embed_documents(chunks)
            vector_store.insert_documents(doc_embeddings, chunks)
            vector_store.create_index()
            vector_store.load_collection()
            return True

        result = await asyncio.to_thread(blocking_store)
        return result
    except Exception as e:
        print(f"Error storing documents in vector store: {e}")
        return False



async def search_in_vector_store(user_input, top_k=5, similarity_threshold=0.5):
    try:
        azure_embedding = connect_azure_embedding()
        embeddings = azure_embedding["model"]
        vector_store = Zilliz(
            embedding_function=embeddings,
            collection_name="research_docs",
            connection_args={
                "uri": ZILLIZ_CLOUD_URI,
                "token": ZILLIZ_CLOUD_TOKEN
            },
            text_field="text",
            vector_field="embedding"   
        )
        results = await vector_store.asimilarity_search_with_score(
            user_input,
            k=top_k
        )
        # output = []
        result = ""
        for doc, score in results:
            similarity = 1 / (1 + score)  # Convert distance to similarity (0 to 1)
            if similarity > similarity_threshold:
                # output.append({
                #     "content": doc.page_content,
                #     "metadata": doc.metadata,
                #     "score": similarity
                # })
                result += doc.page_content + "\n"
        return result
    except Exception as e:
        print("Error:", e)
        return ""
 