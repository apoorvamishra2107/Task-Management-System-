from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

DATA_FILE = 'tasks.json'

# Initialize tasks file if it doesn't exist
def init_data_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump([], f)

# Load tasks from file
def load_tasks():
    init_data_file()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

# Save tasks to file
def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

# Route to serve the frontend
@app.route('/')
def home():
    return render_template('index.html')

# GET all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify({
        'success': True,
        'tasks': tasks,
        'count': len(tasks)
    }), 200

# GET single task by ID
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t['id'] == task_id), None)
    
    if task:
        return jsonify({
            'success': True,
            'task': task
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': 'Task not found'
        }), 404

# POST create new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({
            'success': False,
            'message': 'Title is required'
        }), 400
    
    tasks = load_tasks()
    
    # Generate new ID
    new_id = max([t['id'] for t in tasks], default=0) + 1
    
    new_task = {
        'id': new_id,
        'title': data['title'],
        'description': data.get('description', ''),
        'status': data.get('status', 'pending'),
        'priority': data.get('priority', 'medium'),
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    tasks.append(new_task)
    save_tasks(tasks)
    
    return jsonify({
        'success': True,
        'message': 'Task created successfully',
        'task': new_task
    }), 201

# PUT update task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    tasks = load_tasks()
    
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        return jsonify({
            'success': False,
            'message': 'Task not found'
        }), 404
    
    # Update task fields
    if 'title' in data:
        tasks[task_index]['title'] = data['title']
    if 'description' in data:
        tasks[task_index]['description'] = data['description']
    if 'status' in data:
        tasks[task_index]['status'] = data['status']
    if 'priority' in data:
        tasks[task_index]['priority'] = data['priority']
    
    tasks[task_index]['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    save_tasks(tasks)
    
    return jsonify({
        'success': True,
        'message': 'Task updated successfully',
        'task': tasks[task_index]
    }), 200

# DELETE task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    
    task_index = next((i for i, t in enumerate(tasks) if t['id'] == task_id), None)
    
    if task_index is None:
        return jsonify({
            'success': False,
            'message': 'Task not found'
        }), 404
    
    deleted_task = tasks.pop(task_index)
    save_tasks(tasks)
    
    return jsonify({
        'success': True,
        'message': 'Task deleted successfully',
        'task': deleted_task
    }), 200

# GET tasks by status
@app.route('/api/tasks/status/<string:status>', methods=['GET'])
def get_tasks_by_status(status):
    tasks = load_tasks()
    filtered_tasks = [t for t in tasks if t['status'].lower() == status.lower()]
    
    return jsonify({
        'success': True,
        'tasks': filtered_tasks,
        'count': len(filtered_tasks)
    }), 200

if __name__ == '__main__':
    init_data_file()
    app.run(debug=True, port=5000)