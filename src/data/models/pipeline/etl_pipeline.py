from typing import List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import DataGenerationError
from src.db.session import get_db
from src.data.generators.product_generator import ProductGenerator
from src.data.generators.store_generator import StoreGenerator
from src.data.generators.transaction_generator import TransactionGenerator
from src.data.generators.inventory_generator import InventoryGenerator
from src.data.pipeline.data_validator import DataValidator
from src.data.pipeline.data_cleaner import DataCleaner

logger = get_logger(__name__)


class ETLPipeline:
    """ETL Pipeline for supermarket data"""

    def __init__(self):
        self.validator = DataValidator()
        self.cleaner = DataCleaner()

    def run(self) -> Dict[str, Any]:
        """Run the ETL pipeline"""
        logger.info("Starting ETL Pipeline...")

        try:
            # Generate data
            logger.info("Generating data...")
            products = self._generate_products()
            stores = self._generate_stores()
            transactions = self._generate_transactions(products, stores)
            inventory = self._generate_inventory(products, stores)

            # Validate data
            logger.info("Validating data...")
            self.validator.validate_products(products)
            self.validator.validate_stores(stores)
            self.validator.validate_transactions(transactions)
            self.validator.validate_inventory(inventory)

            # Clean data
            logger.info("Cleaning data...")
            products = self.cleaner.clean_products(products)
            stores = self.cleaner.clean_stores(stores)
            transactions = self.cleaner.clean_transactions(transactions)
            inventory = self.cleaner.clean_inventory(inventory)

            # Load data to database
            logger.info("Loading data to database...")
            self._load_data(products, stores, transactions, inventory)

            logger.info("ETL Pipeline completed successfully")
            return {
                "status": "success",
                "stats": {
                    "products": len(products),
                    "stores": len(stores),
                    "transactions": len(transactions),
                    "inventory": len(inventory),
                }
            }

        except Exception as e:
            logger.error(f"ETL Pipeline failed: {str(e)}")
            raise DataGenerationError(f"ETL Pipeline failed: {str(e)}")

    def _generate_products(self) -> List[Dict[str, Any]]:
        """Generate product data"""
        generator = ProductGenerator(num_products=500)
        return generator.generate_batch(batch_size=500)

    def _generate_stores(self) -> List[Dict[str, Any]]:
        """Generate store data"""
        generator = StoreGenerator(num_stores=10)
        return generator.generate_batch(batch_size=10)

    def _generate_transactions(
        self, products: List[Dict], stores: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate transaction data"""
        product_ids = [p["id"] for p in products]
        store_ids = [s["id"] for s in stores]

        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years of data

        generator = TransactionGenerator(
            product_ids=product_ids,
            store_ids=store_ids,
            start_date=start_date,
            end_date=end_date,
            num_transactions=50000,
        )
        return generator.generate_batch(batch_size=50000)

    def _generate_inventory(
        self, products: List[Dict], stores: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate inventory data"""
        product_ids = [p["id"] for p in products]
        store_ids = [s["id"] for s in stores]

        generator = InventoryGenerator(
            product_ids=product_ids,
            store_ids=store_ids,
            num_days=30,
        )
        return generator.generate_batch()

    def _load_data(
        self,
        products: List[Dict],
        stores: List[Dict],
        transactions: List[Dict],
        inventory: List[Dict],
    ) -> None:
        """Load data to database"""
        db = next(get_db())

        try:
            # Load products
            self._load_products(db, products)
            # Load stores
            self._load_stores(db, stores)
            # Load inventory
            self._load_inventory(db, inventory)
            # Load transactions
            self._load_transactions(db, transactions)

            db.commit()
            logger.info("Data loaded successfully")

        except Exception as e:
            db.rollback()
            logger.error(f"Error loading data: {str(e)}")
            raise

        finally:
            db.close()

    def _load_products(self, db: Session, products: List[Dict]) -> None:
        """Load products to database"""
        from src.data.models.product import Product

        for product_data in products:
            # Check if product already exists
            existing = db.query(Product).filter(Product.sku == product_data["sku"]).first()
            if not existing:
                product = Product(**product_data)
                db.add(product)

    def _load_stores(self, db: Session, stores: List[Dict]) -> None:
        """Load stores to database"""
        from src.data.models.store import Store

        for store_data in stores:
            existing = db.query(Store).filter(Store.code == store_data["code"]).first()
            if not existing:
                store = Store(**store_data)
                db.add(store)

    def _load_inventory(self, db: Session, inventory: List[Dict]) -> None:
        """Load inventory to database"""
        from src.data.models.inventory import Inventory

        for inv_data in inventory:
            inventory_record = Inventory(**inv_data)
            db.add(inventory_record)

    def _load_transactions(self, db: Session, transactions: List[Dict]) -> None:
        """Load transactions to database"""
        from src.data.models.transaction import Transaction

        # Process in batches
        batch_size = 1000
        for i in range(0, len(transactions), batch_size):
            batch = transactions[i:i + batch_size]
            for tx_data in batch:
                transaction = Transaction(**tx_data)
                db.add(transaction)
            db.flush()