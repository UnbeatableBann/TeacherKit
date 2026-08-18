import csv
import io

from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings_client import get_embeddings
from app.models.domain import Product, ProductEmbedding


async def ingest_csv(tenant_id: str, csv_content: str, db: AsyncSession):
    reader = csv.DictReader(io.StringIO(csv_content))
    
    products_to_add = []
    descriptions = []
    
    for row in reader:
        specs = {}
        for k, v in row.items():
            if k not in ["name", "category", "price", "currency", "stock_status", "description"]:
                specs[k] = v
                
        product = Product(
            tenant_id=tenant_id,
            name=row["name"],
            category=row.get("category", "General"),
            price=float(row.get("price", 0)),
            currency=row.get("currency", "USD"),
            stock_status=row.get("stock_status", "in_stock"),
            description=row.get("description", ""),
            specs=specs
        )
        products_to_add.append(product)
        descriptions.append(product.description + " " + " ".join([f"{k}:{v}" for k,v in specs.items()]))
        
    db.add_all(products_to_add)
    await db.flush()
    
    # Generate embeddings
    embeddings = await get_embeddings(descriptions)
    
    emb_records = []
    for prod, emb in zip(products_to_add, embeddings):
        emb_records.append(ProductEmbedding(
            product_id=prod.id,
            embedding=emb,
            embedding_model_version="voyage-large-2"
        ))
        
    db.add_all(emb_records)
    await db.commit()
