import re
import json
import os

# Get path to raw.txt in the same folder as the script
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, 'raw.txt')

# Read the receipt file
with open(file_path, 'r') as file:
    text = file.read()

# Extract date and time
date_pattern = r"Date:\s*(\d{4}-\d{2}-\d{2})\s*(\d{2}:\d{2})"
date_match = re.search(date_pattern, text)
date = date_match.group(1) if date_match else ""
time = date_match.group(2) if date_match else ""

# Extract products and prices
item_pattern = r"-\s*(.*?)\s+(\d+(\.\d+)?)"
items = re.findall(item_pattern, text)
products = [{"name": i[0], "price": float(i[1])} for i in items]

# Calculate total price
total = sum(p['price'] for p in products)

# Extract payment method
payment_pattern = r"Payment Method:\s*(.*)"
payment_match = re.search(payment_pattern, text)
payment_method = payment_match.group(1) if payment_match else ""

# Create structured receipt data
receipt_data = {
    "date": date,
    "time": time,
    "products": products,
    "total": total,
    "payment_method": payment_method
}

# Print JSON output
print(json.dumps(receipt_data, indent=4))