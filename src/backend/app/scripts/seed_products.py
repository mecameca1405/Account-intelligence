import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db.database import sessionLocal
from ..models.product_category import ProductCategory
from ..models.hpe_product import HPEProduct
from ..models.industry import Industry


# ==========================================================
# MASTER SEED – INDUSTRIES + HPE CATALOG
# Idempotent, safe for multiple executions
# ==========================================================


async def seed_master_data():
    async with sessionLocal() as db:  # AsyncSession

        print("🌱 Starting master seed...")

        # ======================================================
        # 1️⃣ INDUSTRIES
        # ======================================================

        industries_data = [
            {
                "name": "Retail",
                "description": "Consumer-facing businesses operating physical and digital commerce environments."
            },
            {
                "name": "Financial Services",
                "description": "Banking, insurance, fintech, and capital markets organizations requiring secure, high-availability infrastructure."
            },
            {
                "name": "Manufacturing",
                "description": "Industrial and production organizations leveraging automation, IoT, and predictive analytics."
            },
            {
                "name": "Healthcare",
                "description": "Hospitals, pharma, and life sciences organizations requiring compliant, secure, and high-performance systems."
            },
            {
                "name": "Telecommunications",
                "description": "Connectivity providers operating distributed, edge-intensive network environments."
            },
            {
                "name": "Energy",
                "description": "Oil, gas, utilities, and renewable energy companies managing critical infrastructure and large data volumes."
            },
        ]

        for ind in industries_data:
            stmt = select(Industry).where(Industry.name == ind["name"])
            existing = (await db.execute(stmt)).scalar_one_or_none()

            if not existing:
                db.add(Industry(**ind))

        await db.flush()

        # ======================================================
        # 2️⃣ PRODUCT CATEGORIES
        # ======================================================

        categories_data = [
            {
                "name": "Compute",
                "description": "High-performance enterprise servers and workload-optimized compute solutions."
            },
            {
                "name": "Storage",
                "description": "AI-driven, data-centric storage for hybrid cloud environments."
            },
            {
                "name": "Networking",
                "description": "Secure edge-to-cloud networking powered by Aruba."
            },
            {
                "name": "Hybrid Cloud",
                "description": "Cloud services delivering consumption-based IT models."
            },
            {
                "name": "Data & AI",
                "description": "Advanced analytics and AI infrastructure platforms."
            },
            {
                "name": "Edge",
                "description": "Ruggedized and distributed compute for real-time processing."
            },
        ]

        inserted_categories = {}

        for cat in categories_data:
            stmt = select(ProductCategory).where(ProductCategory.name == cat["name"])
            existing = (await db.execute(stmt)).scalar_one_or_none()

            if not existing:
                new_cat = ProductCategory(**cat)
                db.add(new_cat)
                await db.flush()
                inserted_categories[cat["name"]] = new_cat
            else:
                inserted_categories[cat["name"]] = existing

        # ======================================================
        # 3️⃣ HPE PRODUCTS
        # ======================================================

        products_data = [

            # COMPUTE
            {
                "name": "HPE ProLiant DL380 Gen11",
                "category": "Compute",
                "description": "Dual-socket 2U rack server optimized for enterprise workloads.",
                "business_value": "Improves workload performance while reducing infrastructure risk.",
                "product_url": "https://www.hpe.com/us/en/product-catalog/servers/proliant-servers.html"
            },
            {
                "name": "HPE Apollo 6500",
                "category": "Compute",
                "description": "High-performance AI and GPU-optimized compute platform.",
                "business_value": "Accelerates AI training and analytics workloads.",
                "product_url": "https://www.hpe.com/us/en/high-performance-computing.html"
            },

            # STORAGE
            {
                "name": "HPE Alletra 6000",
                "category": "Storage",
                "description": "Cloud-native storage platform powered by AI.",
                "business_value": "Reduces downtime and simplifies hybrid storage operations.",
                "product_url": "https://www.hpe.com/us/en/storage/alletra.html"
            },

            # NETWORKING
            {
                "name": "HPE Aruba CX 6300",
                "category": "Networking",
                "description": "Enterprise-grade intelligent switching solution.",
                "business_value": "Enables scalable, automated campus networking.",
                "product_url": "https://www.arubanetworks.com/"
            },

            # HYBRID CLOUD
            {
                "name": "HPE GreenLake",
                "category": "Hybrid Cloud",
                "description": "Edge-to-cloud consumption-based IT platform.",
                "business_value": "Transforms CapEx into predictable OpEx consumption model.",
                "product_url": "https://www.hpe.com/us/en/greenlake.html"
            },
            {
                "name": "HPE Private Cloud Enterprise",
                "category": "Hybrid Cloud",
                "description": "Enterprise private cloud delivered as-a-service.",
                "business_value": "Combines cloud agility with enterprise control and compliance.",
                "product_url": "https://www.hpe.com/us/en/greenlake/private-cloud-enterprise.html"
            },

            # DATA & AI
            {
                "name": "HPE Ezmeral Data Fabric",
                "category": "Data & AI",
                "description": "Hybrid data fabric for AI and analytics.",
                "business_value": "Eliminates data silos across edge, core, and cloud.",
                "product_url": "https://www.hpe.com/us/en/software/ezmeral.html"
            },

            # EDGE
            {
                "name": "HPE Edgeline EL8000",
                "category": "Edge",
                "description": "Converged edge system for harsh environments.",
                "business_value": "Enables real-time analytics at the point of data generation.",
                "product_url": "https://www.hpe.com/us/en/servers/edgeline.html"
            },
        ]

        for prod in products_data:

            stmt = select(HPEProduct).where(HPEProduct.name == prod["name"])
            existing = (await db.execute(stmt)).scalar_one_or_none()

            if existing:
                continue

            category = inserted_categories.get(prod["category"])
            if not category:
                raise ValueError(f"Category {prod['category']} not found.")

            new_product = HPEProduct(
                name=prod["name"],
                category_id=category.id,
                description=prod["description"],
                business_value=prod["business_value"],
                product_url=prod["product_url"],
                is_simulated=True,
            )

            db.add(new_product)

        await db.commit()

        print("✅ Master seed completed successfully!")


# ==========================================================
# RUNNER
# ==========================================================

if __name__ == "__main__":
    asyncio.run(seed_master_data())