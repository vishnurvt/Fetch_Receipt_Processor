from flask import Flask, request, jsonify
import math
import uuid

app = Flask(__name__)

# In-memory storage for receipts and points
receipts = {}

# Helper function to calculate points based on given rules
def calculate_points(receipt):
    points = 0

    # Rule 1: 1 point for every alphanumeric character in the retailer name
    for char in receipt["retailer"]:
        points += sum(char.isalnum())

    # Rule 2: 50 points if the total is a round dollar amount with no cents
    if receipt["total"].endswith(".00"):
        points += 50

    # Rule 3: 25 points if the total is a multiple of 0.25
    if float(receipt["total"]) % 0.25 == 0:
        points += 25

    # Rule 4: 5 points for every two items on the receipt
    points += len(receipt["items"]) // 2 * 5

    # Rule 5: If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2
    # and round up to the nearest integer. The result is the number of points earned.
    for item in receipt["items"]:
        trimmed_length = len(item["shortDescription"].strip())
        if trimmed_length % 3 == 0:
            points += int(math.ceil(float(item["price"]) * 0.2))

    # Rule 6: 6 points if the day in the purchase date is odd
    purchase_date = receipt["purchaseDate"]
    day = int(purchase_date.split("-")[2])
    if day % 2 != 0:
        points += 6

    # Rule 7: 10 points if the time of purchase is after 2:00pm (14:00) and before 4:00pm (16:00)
    purchase_time = receipt["purchaseTime"]
    hour = int(purchase_time.split(":")[0])
    if 14 <= hour <= 16:
        points += 10

    return points

# Endpoint to process a receipt
@app.route("/receipts/process", methods=["POST"])
def process_receipt():
    receipt = request.json
    
    # Validate the receipt JSON
    if not all(key in receipt for key in ["retailer", "purchaseDate", "purchaseTime", "items", "total"]):
        return jsonify({"error": "Invalid receipt"}), 400

    # Generate a unique ID for the receipt
    receipt_id = str(uuid.uuid4())

    # Calculate the points for the receipt
    points = calculate_points(receipt)

    # Store the receipt and points in memory
    receipts[receipt_id] = points

    return jsonify({"id": receipt_id}), 200

# Endpoint to get the points awarded for a receipt
@app.route("/receipts/<string:id>/points", methods=["GET"])
def get_points(id):
    if id in receipts:
        points = receipts[id]
        return jsonify({"points": points}), 200
    else:
        return jsonify({"error": "Receipt not found"}), 404

if __name__ == "__main__":
    app.run()