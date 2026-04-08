from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str
    country: str


class User(BaseModel):
    name: str
    age: int
    address: Address # Nested model( refrence of class Address)


address_data =Address(
    street="123 Main St",
    city="Anytown", 
    country="USA"
    )

user_data = User(
    name="John Doe",
    age=30,
    address=address_data
    )

print(user_data)