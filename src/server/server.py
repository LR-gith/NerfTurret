import base64
import io
import os
import sys

import cv2
import numpy as np
from dotenv import load_dotenv
from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request
from flask import send_file
from flask import send_from_directory
from flask_socketio import SocketIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.detection.color_detection import ColorDetection
from src.detection.object_detection import ObjectDetection
from src.exception.exception import UnrecognizedDetectorException

app = Flask(__name__)
socketio = SocketIO(app)
no_value_set_constant = "No value set yet"
stored_value = {"value": no_value_set_constant}
redirectToColorSelection = {"redirect": False}
current_image = None
current_mask = None
current_values = {
    'conf': no_value_set_constant,
    'x': no_value_set_constant,
    'y': no_value_set_constant,
    'relative_x_angle': no_value_set_constant,
    'relative_y_angle': no_value_set_constant,
    'absolut_x_angle': no_value_set_constant,
    'absolut_y_angle': no_value_set_constant
}
color_selections = {"status": "", "colors": []}


@app.route('/')
def homepage():
    return render_template('templates/index.html', value=stored_value['value'])


@app.route('/colorSelector')
def color_selector():
    return render_template('templates/color_selector.html')


@app.route('/ping', methods=['GET'])
def ping():
    return "pong"


@app.route('/updateObjectDetection', methods=['POST'])
def update_object_detection():
    global current_image, current_values
    if 'image' not in request.files:
        return jsonify({"error": "Missing image in request"}), 400

    image_file = request.files['image']
    current_image = decode_image(image_file)
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
    current_image = decode_image(image_file)

    mask_file = request.files['mask']
    current_mask = decode_image(mask_file)
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


@app.route('/calculateDetection', methods=['POST'])
def calculate_detection():
    global current_image, current_mask, current_values
    image_file = request.files['image']
    frame = decode_image(image_file)

    website_running = bool(request.form.get('website_running'))
    detector_class = str(request.form.get('detector_class'))
    detector_target_class = str(request.form.get('detector_target_class'))
    detector_color_range = int(request.form.get('detector_color_range'))
    detector_camera_width = int(request.form.get("detector_camera_width"))
    detector_camera_height = int(request.form.get("detector_camera_height"))
    detector_camera_width_angle = int(
        request.form.get("detector_camera_width_angle"))
    detector_camera_height_angle = int(
        request.form.get("detector_camera_height_angle"))
    detector_show_img = bool(request.form.get('detector_show_img'))
    absolut_x_angle = int(request.form.get('absolut_x_angle'))
    absolut_y_angle = int(request.form.get('absolut_y_angle'))

    if detector_class == "ObjectDetection":
        detector = ObjectDetection(target_class=detector_target_class,
                                   website_running=website_running,
                                   camera_size=(detector_camera_width,
                                                detector_camera_height),
                                   camera_bandwidth=(
                                       detector_camera_width_angle,
                                       detector_camera_height_angle),
                                   show_img=detector_show_img
                                   )
    elif detector_class == "ColorDetection":
        detector = ColorDetection(target_class=detector_target_class,
                                  color_range=detector_color_range,
                                  website_running=website_running,
                                  camera_size=(detector_camera_width,
                                               detector_camera_height),
                                  camera_bandwidth=(detector_camera_width_angle,
                                                    detector_camera_height_angle),
                                  show_img=detector_show_img
                                  )
    else:
        raise UnrecognizedDetectorException("Unrecognized class for detector")
    result_frame, mask, values = detector.detect(frame)

    values['absolut_x_angle'] = int(
        np.clip(absolut_x_angle + values['relative_x_angle'], 0, 180))
    values['absolut_y_angle'] = int(
        np.clip(absolut_y_angle + values['relative_y_angle'], 60, 120))
    current_image = result_frame
    current_values = values
    if mask is not None:
        current_mask = mask
        socketio.emit('updateColorDetection', {
            'values': current_values,
            'both_image_updated': True
        })
    else:
        socketio.emit('updateObjectDetection', {
            'values': current_values,
            'image_updated': True
        })

    return jsonify({"values": values}), 200


def encode_image(img):
    _, buffer = cv2.imencode('.jpg', img)
    return base64.b64encode(buffer).decode('utf-8')


def decode_image(image_file):
    img_bytes = image_file.read()
    image_array = np.frombuffer(img_bytes, np.uint8)
    return cv2.imdecode(image_array, cv2.IMREAD_COLOR)


@app.route('/updateOnlyImage', methods=['POST'])
def update_only_image():
    global current_image
    if 'image' not in request.files:
        return jsonify({"error": "Missing one of the images in request"}), 400

    image_file = request.files['image']
    current_image = decode_image(image_file)
    return jsonify({"status": "ok"}), 200


@app.route('/get_color_selection_list')
def get_color_selection_list():
    global color_selections
    if not color_selections["colors"]:
        color_selections["status"] = "waiting"
    else:
        color_selections["status"] = "ok"
    return jsonify(color_selections)


@app.route('/clear_color_selection')
def clear_color_selection():
    global color_selections
    color_selections["status"] = ""
    color_selections["colors"] = []
    return jsonify(color_selections)


@app.route('/updateColorSelections', methods=['POST'])
def update_color_selections():
    global color_selections
    json = request.get_json()
    if 'colors' not in json:
        return jsonify({"error": "Missing color data"}), 400

    color_selections["colors"] = json["colors"]
    return jsonify({"status": "ok"})


@app.route('/redirectToColorSelection', methods=['GET'])
def redirect_to_color_selection():
    try:
        socketio.emit('redirectToColorSelection')
    except Exception as exception:
        print(exception)
        return jsonify({"status": "failed"})
    return jsonify({"status": "redirected"})


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
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(env_path)
    PORT = int(os.getenv('PORT'))
    app.run(host='0.0.0.0', port=PORT, debug=True)
