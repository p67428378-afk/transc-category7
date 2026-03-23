from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TransactionBase(BaseModel):
    date: datetime
    description: str
    amount: float
    currency: Optional[str] = "USD"
    raw_data_source: Optional[str] = None
    status: Optional[str] = "processing"
    reference_id: Optional[str] = None

class TransactionCreate(TransactionBase):
    user_id: int

class Transaction(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    user_id: Optional[int] = None

class Category(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CategorizedTransactionBase(BaseModel):
    transaction_id: int
    category_id: int
    categorization_method: Optional[str] = "LLM"
    confidence_score: Optional[float] = None
    llm_explanation: Optional[str] = None
    customer_explanation: Optional[str] = None

class CategorizedTransactionCreate(CategorizedTransactionBase):
    pass

class CategorizedTransaction(CategorizedTransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    categorized_at: Optional[datetime] = None
