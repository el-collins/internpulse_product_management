# app.routers.product.py

from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from app.models import Product, ProductCreate, ProductUpdate
from app.database import get_db, products_collection

from bson import ObjectId

router = APIRouter()



@router.post("/products/", response_model=Product, status_code=201)
async def create_product(product: ProductCreate, db=Depends(get_db)):
    """Create a new product."""
    # Check if product with same name exists
    existing_product = await products_collection.find_one({"name": product.name})
    if existing_product:
        raise HTTPException(status_code=400, detail="Product with this name already exists")
    
    # Convert Decimal to str for MongoDB storage
    product_dict = product.model_dump()
    product_dict['price'] = str(product_dict['price'])
    
    new_product = await products_collection.insert_one(product_dict)
    created_product = await products_collection.find_one({"_id": new_product.inserted_id})
    
    # Convert price back to Decimal
    created_product['price'] = Decimal(created_product['price'])
    return created_product


@router.get("/products/", response_model=List[Product])
async def get_products(
    name: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db=Depends(get_db)
):
    """Get products with optional filtering."""
    query = {}
    
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if min_price is not None or max_price is not None:
        query["price"] = {}
        if min_price is not None:
            query["price"]["$gte"] = str(min_price)
        if max_price is not None:
            query["price"]["$lte"] = str(max_price)

    products = await products_collection.find(query).to_list(None)
    
    # Convert price strings to Decimal
    for product in products:
        product['price'] = Decimal(product['price'])
    
    if not products:
        raise HTTPException(status_code=404, detail="No products found matching the criteria")
    return products


@router.get("/products/{product_id}", response_model=Product)
async def get_product_by_id(product_id: str, db=Depends(get_db)):
    """Get a product by ID."""
    try:
        product = await products_collection.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        product['price'] = Decimal(product['price'])
        return product
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

@router.put("/products/{product_id}", response_model=Product)
async def update_product_by_id(
    product_id: str, 
    product_update: ProductUpdate,
    db=Depends(get_db)
):
    """Update a product by ID."""
    try:
        # Remove None values from the update
        update_data = {k: v for k, v in product_update.model_dump(exclude_unset=True).items()}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid update data provided")

        # Check name uniqueness if name is being updated
        if "name" in update_data:
            existing_product = await products_collection.find_one({
                "name": update_data["name"],
                "_id": {"$ne": ObjectId(product_id)}
            })
            if existing_product:
                raise HTTPException(status_code=400, detail="Product with this name already exists")

        # Convert price to string if it exists in update data
        if "price" in update_data:
            update_data["price"] = str(update_data["price"])

        update_result = await products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        
        updated_product = await products_collection.find_one({"_id": ObjectId(product_id)})
        updated_product['price'] = Decimal(updated_product['price'])
        return updated_product
    except HTTPException:
        raise
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

@router.delete("/products/{product_id}", status_code=204)
async def delete_product_by_id(product_id: str, db=Depends(get_db)):
    """Delete a product by ID."""
    try:
        delete_result = await products_collection.delete_one({"_id": ObjectId(product_id)})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")