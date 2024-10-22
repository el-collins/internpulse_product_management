from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Annotated
from bson import ObjectId
from pydantic import BeforeValidator

# Custom type for MongoDB ObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None

class Product(ProductBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")