from typing import Dict, Any

def check_stock(args: Dict[str, Any]) -> str:
    """Kiểm tra số lượng tồn kho của sản phẩm."""
    item = args.get("item_name", "").lower()
    if not item:
        return "Error: 'item_name' is a required argument."

    inventory = {"iphone": 10, "macbook": 5, "airpods": 0}
    
    if item in inventory:
        return f"{item} is in stock. Quantity available: {inventory[item]}."
    return f"Item '{item}' is out of stock or not found."

def get_discount(args: Dict[str, Any]) -> str:
    """Kiểm tra mã giảm giá."""
    code = args.get("coupon_code", "").upper()
    if not code:
        return "Error: 'coupon_code' is a required argument."

    if code == "WINNER":
        return "Code valid. 10% discount applied."
    return "Invalid discount code. 0% discount."

def calc_shipping(args: Dict[str, Any]) -> str:
    """Tính phí giao hàng."""
    destination = args.get("destination", "").lower()
    weight_kg = args.get("weight_kg", 0)

    if destination == "hanoi":
        cost = 5 + (weight_kg * 1) # $5 base + $1 per kg
        return f"Shipping cost to Hanoi for a {weight_kg}kg package is ${cost}."
    return f"Shipping cost for a {weight_kg}kg package is ${15 + (weight_kg * 2)}."

# Danh sách tools để nạp vào ReActAgent
ECOMMERCE_TOOLS = [
    {
        "name": "check_stock",
        "description": "Use this to check the available quantity of an item. Argument MUST be a JSON string with one key: 'item_name'. Example: '{\"item_name\": \"iphone\"}'",
        "func": check_stock
    },
    {
        "name": "get_discount",
        "description": "Use this to get the discount percentage for a coupon code. Argument MUST be a JSON string with one key: 'coupon_code'. Example: '{\"coupon_code\": \"WINNER\"}'",
        "func": get_discount
    },
    {
        "name": "calc_shipping",
        "description": "Calculates shipping cost based on destination and weight. Argument MUST be a JSON string with two keys: 'destination' (string) and 'weight_kg' (float). Example: '{\"destination\": \"hanoi\", \"weight_kg\": 0.4}'",
        "func": calc_shipping
    }
]