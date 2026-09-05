from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import numpy as np
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import RAGError

logger = get_logger(__name__)


class VectorStore:
    """Vector store for RAG"""

    def __init__(
        self,
        collection_name: str = settings.RAG_COLLECTION_NAME,
        persist_directory: str = "./chromadb_data",
    ):
        try:
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            ))
            self.collection_name = collection_name
            self.collection = self._get_or_create_collection()
            logger.info(f"Connected to vector store: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {str(e)}")
            raise RAGError(f"Vector store initialization failed: {str(e)}")

    def _get_or_create_collection(self) -> chromadb.Collection:
        """Get or create a collection"""
        try:
            embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name=settings.EMBEDDING_MODEL,
            )

            if self.collection_name in self.client.list_collections():
                return self.client.get_collection(
                    name=self.collection_name,
                    embedding_function=embedding_fn,
                )
            else:
                return self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=embedding_fn,
                )
        except Exception as e:
            logger.error(f"Error getting/creating collection: {str(e)}")
            raise RAGError(f"Collection operation failed: {str(e)}")

    def add_documents(
        self,
        documents: List[Dict[str, Any]],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Add documents to vector store"""
        try:
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(documents))]

            texts = [doc["text"] if isinstance(doc, dict) else str(doc) for doc in documents]

            self.collection.add(
                documents=texts,
                ids=ids,
                metadatas=metadatas,
            )
            logger.info(f"Added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise RAGError(f"Document addition failed: {str(e)}")

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query the vector store"""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=top_k,
                where=filter,
            )

            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "distance": results["distances"][0][i] if "distances" in results else None,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                }
                formatted_results.append(result)

            logger.info(f"Query returned {len(formatted_results)} results")
            return formatted_results
        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            raise RAGError(f"Query failed: {str(e)}")

    def delete_collection(self) -> None:
        """Delete the collection"""
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}")
            raise RAGError(f"Collection deletion failed: {str(e)}")