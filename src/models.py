from typing import List, Optional
from pydantic import BaseModel, Field
class PaymentMethod(BaseModel):
    type: Optional[int] = Field(default=None, description="Type of payment method")
    last4: Optional[str] = Field(default=None, description="Last 4 digits of the payment method")

class Merchant(BaseModel):
    name: Optional[str] = Field(default=None, description="Name of the merchant")
    country: Optional[str] = Field(default=None, description="Country of the merchant. If not explicitly mentioned, make an educated guess based on the context.")
    city: Optional[str] = Field(default=None, description="City of the merchant. If not explicitly mentioned, make an educated guess based on the context.")
    street: Optional[str] = Field(default=None, description="Street address of the merchant")
    phoneNumber: Optional[str] = Field(default=None, description="Phone number of the merchant")

class Item(BaseModel):
    itemName: Optional[str] = Field(default=None, description="Name of the item")
    itemDescription: Optional[str] = Field(default=None, description="Description of the item. If not provided, infer a brief description based on the item name and context.")
    category: Optional[str] = Field(default=None, description="Category of the item. If not provided, infer a suitable category based on the item name and context.")
    generalCategory: Optional[str] = Field(default=None, description="General category of the item. If not provided, infer a broader category based on the item name and context.")
    unit: Optional[str] = Field(default=None, description="Unit of measurement for the item")
    quantity: Optional[float] = Field(default=None, description="Quantity of the item")
    unitPrice: Optional[float] = Field(default=None, description="Unit price of the item")
    totalPrice: Optional[float] = Field(default=None, description="Total price of the item")
    taxRate: Optional[float] = Field(default=None, description="Tax rate applied to the item")

class Receipt(BaseModel):
    purchaseDate: Optional[str] = Field(default=None, description="Date of purchase")
    totalAmount: Optional[float] = Field(default=None, description="Total amount of the purchase")
    taxAmount: Optional[float] = Field(default=None, description="Total tax amount")
    discountAmount: Optional[float] = Field(default=None, description="Total discount amount")
    paymentMethod: Optional[PaymentMethod] = Field(default=None, description="Payment method used")
    merchant: Optional[Merchant] = Field(default=None, description="Merchant information")
    items: Optional[List[Item]] = Field(default=None, description="List of items purchased")

class ReceiptAnalysisResponse(BaseModel):
    amount: Optional[float] = Field(default=None, description="Total amount of the transaction")
    description: Optional[str] = Field(default=None, description="Description of the transaction. If not explicitly provided, generate a brief summary based on the merchant name, items purchased, or other relevant information.")
    transactionType: Optional[int] = Field(default=None, description="Type of transaction")
    receipt: Optional[Receipt] = Field(default=None, description="Detailed receipt information")