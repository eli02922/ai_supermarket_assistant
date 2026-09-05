from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
from .document_processor import DocumentProcessor
from src.core.logging import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class RAGRetriever:
    """RAG retriever for fetching relevant documents"""

    def __init__(self):
        self.vector_store = VectorStore()
        self.document_processor = DocumentProcessor()
        self._initialize_documents()

    def _initialize_documents(self) -> None:
        """Initialize documents in vector store if empty"""
        try:
            # Check if documents exist
            test_query = self.vector_store.query("test", top_k=1)
            if not test_query:
                logger.info("Initializing documents in vector store...")
                documents = self.document_processor.create_supermarket_documents()
                chunks = self.document_processor.process_documents(documents)

                # Prepare for vector store
                texts = [doc.page_content for doc in chunks]
                metadatas = [doc.metadata for doc in chunks]
                ids = [f"doc_{i}" for i in range(len(chunks))]

                self.vector_store.add_documents(
                    documents=texts,
                    ids=ids,
                    metadatas=metadatas,
                )
                logger.info(f"Initialized {len(chunks)} documents")
        except Exception as e:
            logger.warning(f"Document initialization failed: {str(e)}")

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant documents"""
        try:
            results = self.vector_store.query(
                query_text=query,
                top_k=top_k,
                filter=filter,
            )
            return results
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            return []

    def retrieve_context(
        self,
        query: str,
        top_k: int = 3,
    ) -> str:
        """Retrieve context as a single string"""
        results = self.retrieve(query, top_k=top_k)
        if not results:
            return ""

        context = "\n\n".join([
            f"Context {i+1}:\n{result['document']}"
            for i, result in enumerate(results)
        ])
        return context