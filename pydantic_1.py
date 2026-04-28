from pydantic import BaseModel, computed_field

class Product(BaseModel):
   price: float
   quantity: int

   @computed_field
   @property
   def total_price(self) -> float:
        return self.price * self.quantity
    
