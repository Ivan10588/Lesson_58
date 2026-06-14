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

if __name__ == '__main__':
    app.run(debug=True, port=5000)