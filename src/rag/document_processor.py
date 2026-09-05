from typing import List, Dict, Any, Optional
import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader, CSVLoader
from langchain.schema import Document
from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Process documents for RAG"""

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

    def process_documents(
        self,
        documents: List[Document],
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> List[Document]:
        """Process and chunk documents"""
        if chunk_size:
            self.text_splitter.chunk_size = chunk_size
        if chunk_overlap:
            self.text_splitter.chunk_overlap = chunk_overlap

        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks

    def load_documents_from_directory(
        self,
        directory_path: str,
    ) -> List[Document]:
        """Load documents from a directory"""
        documents = []

        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            if filename.endswith(".txt"):
                loader = TextLoader(file_path)
            elif filename.endswith(".csv"):
                loader = CSVLoader(file_path)
            else:
                continue

            try:
                docs = loader.load()
                # Add metadata
                for doc in docs:
                    doc.metadata["source"] = filename
                    doc.metadata["file_type"] = os.path.splitext(filename)[1]
                documents.extend(docs)
            except Exception as e:
                logger.error(f"Error loading {filename}: {str(e)}")

        logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents

    def create_supermarket_documents(self) -> List[Document]:
        """Create documents about supermarket operations"""
        documents = []

        # Product categories documentation
        categories = {
            "Beverages": "Includes soft drinks, juices, water, energy drinks, coffee, and tea. Typically high-volume products with seasonal demand variations.",
            "Food": "Canned goods, pasta, rice, cereals, snacks, and condiments. Essential items with stable demand patterns.",
            "Dairy": "Milk, cheese, yogurt, butter, and eggs. Perishable products with short shelf life requiring careful inventory management.",
            "Meat": "Chicken, pork, beef, seafood, and processed meat. Temperature-controlled products with strict quality requirements.",
            "Produce": "Fresh fruits, vegetables, and herbs. Highly perishable with daily demand fluctuations.",
            "Household": "Cleaning products, laundry supplies, paper products, and kitchen items. Regular purchase items with promotional sensitivity.",
            "Personal Care": "Shampoo, soap, toothpaste, skincare, and deodorant. Brand-loyal categories with stable demand.",
            "Baby Care": "Diapers, formula, baby food, and toiletries. Essential items with consistent demand patterns."
        }

        for category, description in categories.items():
            doc = Document(
                page_content=f"Category: {category}\nDescription: {description}\n"
                            f"Inventory management: Monitor stock levels closely, adjust ordering based on seasonality.",
                metadata={"type": "category", "name": category}
            )
            documents.append(doc)

        # Store operations documentation
        operations_docs = [
            "Store hours: 8:00 AM to 9:00 PM daily.",
            "Delivery schedule: Major deliveries Tuesday and Thursday, with daily top-ups for perishables.",
            "Fresh products: Daily inspection required for produce, meat, and dairy sections.",
            "Seasonal promotions: Holiday seasons (Christmas, New Year, Valentines) require increased stock of relevant products.",
            "Inventory counting: Weekly cycle counts, full inventory every month.",
            "Safety stock policy: Maintain minimum 3 days of safety stock for essentials, 2 days for perishables.",
        ]

        for i, content in enumerate(operations_docs):
            doc = Document(
                page_content=content,
                metadata={"type": "operations", "index": i}
            )
            documents.append(doc)

        # Demand patterns documentation
        demand_patterns = {
            "Weekly patterns": "Higher sales on weekends (Saturday and Sunday). Bulk buying common on weekends.",
            "Monthly patterns": "Payday effect observed at end of month when customers have more spending power.",
            "Seasonal patterns": "December has highest sales due to Christmas. January sees post-holiday decline.",
            "Weather impact": "Rainy season increases demand for comfort foods and warm beverages.",
            "Promotional events": "Promotions typically increase sales by 20-40% for featured products.",
        }

        for title, content in demand_patterns.items():
            doc = Document(
                page_content=f"{title}:\n{content}",
                metadata={"type": "demand_patterns", "title": title}
            )
            documents.append(doc)

        logger.info(f"Created {len(documents)} supermarket documents")
        return documents