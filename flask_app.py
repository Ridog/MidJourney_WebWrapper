from flask import Flask, request, render_template
from flask_socketio import SocketIO, send
from image_processing import process_images, clear_images_directory

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Route for rendering the main prompt form
@app.route("/", methods=['GET'])
def prompt():
    return render_template("prompt.html")

# Route for rendering the final landing page
@app.route("/final_landing", methods=['GET'])
def final_landing():
    return render_template("final_landing.html")

# WebSocket endpoint for notifying the client when the expected number of images are ready
@socketio.on('connect')
def websocket_endpoint():
    def check_images():
        # Determine the expected number of images based on Globals.MODE
        expected_images = 8 if Globals.MODE == "Red Room" else 1

        # Poll for the expected number of images in the /images directory
        while True:
            images_count = len([f for f in os.listdir("images") if os.path.splitext(f)[1].lower() in ('.jpg', '.jpeg', '.png')])
            if images_count == expected_images:
                break
            time.sleep(1)

        # Process the images based on Globals.MODE
        process_images(Globals.MODE)

        # Notify the client when the expected number of images are detected
        send("images_ready")

    socketio.start_background_task(target=check_images)

# Route for processing the user input and generating images
@app.route("/", methods=['POST'])
def process_prompt():
    clear_images_directory("images")
    user_input = request.form.get("prompt")
    # Append the specified string to the user's input
    user_input += Globals.PROMPT_SUFFIX

def start_flask_app():
    socketio.run(app, host='0.0.0.0', port=8000)