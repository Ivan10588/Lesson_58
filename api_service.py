from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
JSON_FILE_PATH = 'data.json'

def load_data():
    if not os.path.exists(JSON_FILE_PATH):
        return []
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_data(data):
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/items', methods=['GET'])
def get_all_items():
    data = load_data()
    return jsonify(data), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    data = load_data()
    item = next((x for x in data if x['id'] == item_id), None)
    if item is None:
        return jsonify({'error': 'Item not found'}), 404
    return jsonify(item), 200

@app.route('/items', methods=['POST'])
def create_item():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    body = request.get_json()
    required_fields = ['name', 'description', 'price']
    if any(k not in body for k in required_fields):
        return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
    
    data = load_data()
    max_id = max((x['id'] for x in data), default=0)
    new_id = max_id + 1
    
    new_item = {
        'id': new_id,
        'name': body['name'],
        'description': body['description'],
        'price': float(body['price'])
    }
    data.append(new_item)
    save_data(data)
    
    return jsonify(new_item), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    body = request.get_json()
    data = load_data()
    
    idx = next((i for i, x in enumerate(data) if x['id'] == item_id), None)
    if idx is None:
        return jsonify({'error': 'Item not found'}), 404

    for key in ['name', 'description', 'price']:
        if key in body:
            if key == 'price':
                data[idx][key] = float(body[key])
            else:
                data[idx][key] = body[key]
    
    save_data(data)
    return jsonify(data[idx]), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    data = load_data()
    initial_len = len(data)
    data = [x for x in data if x['id'] != item_id]
    
    if len(data) == initial_len:
        return jsonify({'error': 'Item not found'}), 404
    
    save_data(data)
    return '', 204

@app.route('/items/filter', methods=['GET'])
def filter_items():
    min_price_str = request.args.get('min_price')
    max_price_str = request.args.get('max_price')
    search_term = request.args.get('search')

    min_price = None
    if min_price_str:
        try:
            min_price = float(min_price_str)
        except ValueError:
            return jsonify({'error': 'min_price must be a number'}), 400

    max_price = None
    if max_price_str:
        try:
            max_price = float(max_price_str)
        except ValueError:
            return jsonify({'error': 'max_price must be a number'}), 400

    all_items = load_data()

    filtered_items = []
    for item in all_items:
        price = item.get('price', 0)
        name_lower = item.get('name', '').lower()
        desc_lower = item.get('description', '').lower()

        if min_price is not None and price < min_price:
            continue

        if max_price is not None and price > max_price:
            continue

        if search_term:
            search_lower = search_term.lower()
            if search_lower not in name_lower and search_lower not in desc_lower:
                continue

        filtered_items.append(item)

    return jsonify(filtered_items), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)