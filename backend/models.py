from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    transactions = relationship("Transaction", back_populates="owner")
    categories = relationship("Category", back_populates="owner")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime(timezone=True))
    description = Column(String)
    amount = Column(Float)
    currency = Column(String, default="USD")
    raw_data_source = Column(String, nullable=True)
    status = Column(String, default="processing") # e.g., processing, failed, successful
    reference_id = Column(String, nullable=True) # For deduplication
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="transactions")
    categorized_data = relationship("CategorizedTransaction", back_populates="transaction_ref", uselist=False)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # For custom categories
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="categories")
    categorized_transactions = relationship("CategorizedTransaction", back_populates="category_ref")

class CategorizedTransaction(Base):
    __tablename__ = "categorized_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    categorization_method = Column(String, default="LLM") # e.g., LLM, Manual
    confidence_score = Column(Float, nullable=True)
    llm_explanation = Column(String, nullable=True)
    customer_explanation = Column(String, nullable=True)
    categorized_at = Column(DateTime(timezone=True), server_default=func.now())

    transaction_ref = relationship("Transaction", back_populates="categorized_data")
    category_ref = relationship("Category", back_populates="categorized_transactions")
