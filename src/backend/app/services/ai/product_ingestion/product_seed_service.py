from sqlalchemy.orm import Session
from sqlalchemy import select

from ....models import HPEProduct, ProductCategory


class ProductSeedService:
    def __init__(self, db: Session):
        self.db = db

    def seed_products(self) -> dict:
        """
        Insert simulated products if they do not already exist.
        """

        products_data = [
            {
                "name": "HPE GreenLake",
                "category": "Cloud Infrastructure",
                "description": "Consumption-based hybrid cloud solution.",
                "business_value": "Reduces CapEx by shifting to OpEx model.",
                "product_url": "https://www.hpe.com/us/en/greenlake.html",
            },
            {
                "name": "HPE ProLiant",
                "category": "Compute",
                "description": "Enterprise-grade high performance servers.",
                "business_value": "Optimized workloads with enterprise reliability.",
                "product_url": "https://www.hpe.com/us/en/servers/proliant.html",
            },
            {
                "name": "HPE Alletra",
                "category": "Storage",
                "description": "High-speed storage solutions for enterprise.",
                "business_value": "Accelerates data-driven applications.",
                "product_url": "https://www.hpe.com/us/en/storage/alletra.html",
            },
            {
                "name": "Aruba Networking",
                "category": "Networking",
                "description": "Secure edge-to-cloud networking platform.",
                "business_value": "Improves secure connectivity across environments.",
                "product_url": "https://www.hpe.com/us/en/networking/aruba.html",
            },
            {
                "name": "HPE AI Infrastructure",
                "category": "Artificial Intelligence",
                "description": "Optimized infrastructure for AI workloads.",
                "business_value": "Accelerates AI deployment and training.",
                "product_url": "https://www.hpe.com/us/en/solutions/artificial-intelligence.html",
            },
            {
                "name": "HPE Data Protection",
                "category": "Security",
                "description": "Enterprise backup and recovery solutions.",
                "business_value": "Ensures business continuity and compliance.",
                "product_url": "https://www.hpe.com/us/en/storage/data-protection.html",
            },
        ]

        created = 0
        skipped = 0

        for product_data in products_data:
            category = self._get_or_create_category(product_data["category"])

            existing_product = self.db.execute(
                select(HPEProduct).where(
                    HPEProduct.name == product_data["name"]
                )
            ).scalar_one_or_none()

            if existing_product:
                skipped += 1
                continue

            new_product = HPEProduct(
                name=product_data["name"],
                category_id=category.id,
                description=product_data["description"],
                business_value=product_data["business_value"],
                product_url=product_data["product_url"],
                is_simulated=True,
            )

            self.db.add(new_product)
            created += 1

        self.db.commit()

        return {
            "created": created,
            "skipped": skipped,
        }

    def _get_or_create_category(self, category_name: str) -> ProductCategory:
        category = self.db.execute(
            select(ProductCategory).where(
                ProductCategory.name == category_name
            )
        ).scalar_one_or_none()

        if category:
            return category

        new_category = ProductCategory(
            name=category_name,
            description=f"{category_name} solutions"
        )

        self.db.add(new_category)
        self.db.commit()

        return new_category