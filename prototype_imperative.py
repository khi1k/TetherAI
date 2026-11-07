# Daily Sales Tracker - Imperative Prototype for Tether AI Technologies

# Sample Data: List of daily sales transactions for a barber shop
sales_data = [
    {"customer": "Alex Mercer", "service": "Haircut", "amount": 30.00},
    {"customer": "Brian Jones", "service": "Beard Trim", "amount": 15.00},
    {"customer": "Alex Mercer", "service": "Hot Towel Shave", "amount": 25.00},
    {"customer": "Carlos Reed", "service": "Haircut", "amount": 30.00},
    {"customer": "Brian Jones", "service": "Shampoo & Style", "amount": 10.00},
    {"customer": "Alex Mercer", "service": "Hair Product", "amount": 18.00},
]

# Mutable state variables for overall summary
overall_subtotal = 0.0
tax_rate = 0.08

# Parallel lists to track customer totals imperatively
customer_names = []
customer_subtotals = []

# Process each sales transaction step-by-step
for transaction in sales_data:
    customer = transaction["customer"]
    amount = transaction["amount"]

    # Accumulate overall subtotal
    overall_subtotal = overall_subtotal + amount

    # Search if customer already exists in our parallel list
    found_index = -1
    current_index = 0
    for name in customer_names:
        if name == customer:
            found_index = current_index
            break
        current_index = current_index + 1

    # Update existing entry or append new customer using if/else
    if found_index != -1:
        current_total = customer_subtotals[found_index]
        customer_subtotals[found_index] = current_total + amount
    else:
        customer_names.append(customer)
        customer_subtotals.append(amount)

# Calculate overall tax and total
overall_tax = overall_subtotal * tax_rate
overall_total = overall_subtotal + overall_tax

# Print Report
print("==================================================")
print("     TETHER AI - DAILY SALES REPORT (IMPERATIVE)  ")
print("==================================================")

print("\n--- Customer Breakdown ---")
idx = 0
for name in customer_names:
    subtotal = customer_subtotals[idx]
    tax = subtotal * tax_rate
    total = subtotal + tax

    print("Customer:", name)
    print(f"  Subtotal: ${subtotal:.2f}")
    print(f"  Tax (8%): ${tax:.2f}")
    print(f"  Total:    ${total:.2f}")
    print("--------------------------------------------------")
    idx = idx + 1

print("\n--- Overall Business Summary ---")
print(f"Subtotal:    ${overall_subtotal:.2f}")
print(f"Tax (8%):    ${overall_tax:.2f}")
print(f"Grand Total: ${overall_total:.2f}")
print("==================================================")
