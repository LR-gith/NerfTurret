import cv2
import numpy as np
from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
from flask_socketio import SocketIO, emit
import io

app = Flask(__name__)
socketio = SocketIO(app)
stored_value = {"value": "No value set yet"}
current_frame = None
current_values = {
    'conf': "No value set yet",
    'x': "No value set yet",
    'y': "No value set yet",
    'x_angle': "No value set yet",
    'y_angle': "No value set yet"
}
@app.route('/')
def homepage():
    return render_template('index.html', value=stored_value['value'])

@app.route('/update', methods=['POST'])
def update_value():
    global current_frame, current_values
    if 'image' not in request.files:
        return jsonify({"error": "Missing image in request"}), 400

    image_file = request.files['image']
    img_bytes = image_file.read()
    image_array = np.frombuffer(img_bytes, np.uint8)
    current_frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    current_values = {
        'conf': request.form.get('conf'),
        'x': request.form.get('x'),
        'y': request.form.get('y'),
        'x_angle': request.form.get('x_angle'),
        'y_angle': request.form.get('y_angle')
    }

    socketio.emit('update', {
        'values': current_values,
        'image_updated': True
    })
    return jsonify({
        "confidence": current_values["conf"],
        "x": current_values["x"],
        "y": current_values["y"],
        "x_angle": current_values["x_angle"],
        "y_angle": current_values["y_angle"],
    }), 200


@app.route('/get_image')
def get_image():
    global current_frame
    if current_frame is None:
        return "No image available", 404

    # Convert frame to JPEG
    ret, buffer = cv2.imencode('.jpg', current_frame)
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
    app.run(host='0.0.0.0', port=5555 ,debug=True)
