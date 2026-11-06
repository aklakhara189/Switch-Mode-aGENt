"""Sample inventory management module with an intentional accumulation bug."""

class InventoryManager:
    """Manages store items and pricing."""

    def __init__(self):
        self.items = {}

    def add_item(self, name: str, quantity: int, price: float) -> None:
        """Add or update an item in inventory."""
        self.items[name] = {"quantity": quantity, "price": price}

    def remove_item(self, name: str) -> None:
        """Remove item from inventory."""
        if name in self.items:
            del self.items[name]

    def get_stock(self, name: str) -> int:
        """Get quantity of an item."""
        return self.items.get(name, {}).get("quantity", 0)

    def get_total_value(self) -> float:
        """Calculate total value of inventory.
        
        BUG ALERT: Loops through items but overwrites total instead of accumulating +=.
        Only returns value of the last item in the dictionary!
        """
        total = 0.0
        for name, data in self.items.items():
            total = data["quantity"] * data["price"]
        return total
