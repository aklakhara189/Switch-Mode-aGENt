"""Production API demonstrating the sample buggy microservices."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .calculator import add, subtract, multiply, divide, calculate_average
from .inventory import InventoryManager

app = FastAPI(title="Sample Production Service", version="1.0.0")
inventory = InventoryManager()

class ItemPayload(BaseModel):
    name: str
    quantity: int
    price: float

@app.get("/calculate")
def calculate(operation: str, a: float, b: float):
    if operation == "add":
        return {"result": add(a, b)}
    elif operation == "subtract":
        return {"result": subtract(a, b)}
    elif operation == "multiply":
        return {"result": multiply(a, b)}
    elif operation == "divide":
        try:
            return {"result": divide(a, b)}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="Invalid operation")

@app.post("/inventory/add")
def add_inventory(item: ItemPayload):
    inventory.add_item(item.name, item.quantity, item.price)
    return {"status": "ok", "message": f"Added {item.name}"}

@app.get("/inventory/total-value")
def total_value():
    return {"total_value": inventory.get_total_value()}
