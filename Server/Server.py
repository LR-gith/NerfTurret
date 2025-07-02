import os

import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_socketio import SocketIO, emit
import io
from dotenv import load_dotenv


app = Flask(__name__)
socketio = SocketIO(app)
stored_value = {"value": "No value set yet"}
current_frame = None
current_mask = None
current_values = {
    'conf': "No value set yet",
    'x': "No value set yet",
    'y': "No value set yet",
    'relative_x_angle': "No value set yet",
    'relative_y_angle': "No value set yet",
    'absolut_x_angle': "No value set yet",
    'absolut_y_angle': "No value set yet"
}
@app.route('/')
def homepage():
    return render_template('index.html', value=stored_value['value'])

@app.route('/ping', methods=['GET'])
def ping():
    return "pong"

@app.route('/updateObjectDetection', methods=['POST'])
def update_object_detection():
    global current_image, current_values
    if 'image' not in request.files:
        return jsonify({"error": "Missing image in request"}), 400

    image_file = request.files['image']
    img_bytes = image_file.read()
    image_array = np.frombuffer(img_bytes, np.uint8)
    current_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    current_values = {
        'conf': request.form.get('conf'),
        'x': request.form.get('x'),
        'y': request.form.get('y'),
        'relative_x_angle': request.form.get('relative_x_angle'),
        'relative_y_angle': request.form.get('relative_y_angle'),
        'absolut_x_angle': request.form.get('absolut_x_angle'),
        'absolut_y_angle': request.form.get('absolut_y_angle')
    }

    socketio.emit('updateObjectDetection', {
        'values': current_values,
        'image_updated': True
    })
    return jsonify({
        "confidence": current_values["conf"],
        "x": current_values["x"],
        "y": current_values["y"],
        "relative_x_angle": current_values["relative_x_angle"],
        "relative_y_angle": current_values["relative_y_angle"],
        "absolut_x_angle": current_values['absolut_x_angle'],
        "absolut_y_angle": current_values['absolut_y_angle']
    }), 200

@app.route('/updateColorDetection', methods=['POST'])
def update_color_detection():
    global current_image, current_mask, current_values
    if 'image' not in request.files or 'mask' not in request.files:
        return jsonify({"error": "Missing one of the images in request"}), 400

    image_file = request.files['image']
    img_bytes = image_file.read()
    image_array = np.frombuffer(img_bytes, np.uint8)
    current_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    mask_file = request.files['mask']
    mask_bytes = mask_file.read()
    mask_array = np.frombuffer(mask_bytes, np.uint8)
    current_mask = cv2.imdecode(mask_array, cv2.IMREAD_COLOR)

    current_values = {
        'conf': request.form.get('conf'),
        'x': request.form.get('x'),
        'y': request.form.get('y'),
        'relative_x_angle': request.form.get('relative_x_angle'),
        'relative_y_angle': request.form.get('relative_y_angle'),
        'absolut_x_angle': request.form.get('absolut_x_angle'),
        'absolut_y_angle': request.form.get('absolut_y_angle')
    }

    socketio.emit('updateColorDetection', {
        'values': current_values,
        'both_image_updated': True
    })
    return jsonify({
        "confidence": current_values["conf"],
        "x": current_values["x"],
        "y": current_values["y"],
        "relative_x_angle": current_values["relative_x_angle"],
        "relative_y_angle": current_values["relative_y_angle"],
        "absolut_x_angle": current_values['absolut_x_angle'],
        "absolut_y_angle": current_values['absolut_y_angle']
    }), 200


@app.route('/get_image')
def get_image():
    global current_image
    if current_image is None:
        return "No image available", 404

    # Convert frame to JPEG
    ret, buffer = cv2.imencode('.jpg', current_image)
    if not ret:
        return "Could not encode image", 500

    return send_file(
        io.BytesIO(buffer.tobytes()),
        mimetype='image/jpeg'
    )

@app.route('/get_mask')
def get_mask():
    global current_mask
    if current_mask is None:
        return "No mask available", 404

    # Convert frame to JPEG
    ret, buffer = cv2.imencode('.jpg', current_mask)
    if not ret:
        return "Could not encode image", 500

    return send_file(
        io.BytesIO(buffer.tobytes()),
        mimetype='image/jpeg'
    )

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/log', methods=['POST'])
def log_message():
    message = request.json["message"]
    socketio.emit('log', message)
    return jsonify({"message": message})

@app.route('/value', methods=['GET'])
def get_value():
    return jsonify({"current_value": stored_value['value']}), 200

if __name__ == '__main__':
    load_dotenv('../.env')
    PORT = os.getenv('PORT')
    app.run(host='0.0.0.0', port=PORT ,debug=True)
