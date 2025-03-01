from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
import datetime
import pandas as pd
import face_recognition

app = Flask(__name__)

# Paths
FACES_DIR = "static/images/faces"
ENCODINGS_FILE = "face_encodings.pkl"
ATTENDANCE_CSV = "attendance.csv"

# Ensure directories exist
os.makedirs(FACES_DIR, exist_ok=True)

# Load or create face encodings
face_encodings = {}
if os.path.exists(ENCODINGS_FILE):
    face_encodings = pd.read_pickle(ENCODINGS_FILE)

# Attendance DataFrame
if os.path.exists(ATTENDANCE_CSV):
    attendance_df = pd.read_csv(ATTENDANCE_CSV)
else:
    attendance_df = pd.DataFrame(columns=["Name", "Timestamp"])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add_face", methods=["POST"])
def add_face():
    name = request.form["name"]
    image = request.files["image"]
    
    # Save image
    image_path = os.path.join(FACES_DIR, f"{name}.jpg")
    image.save(image_path)
    
    # Create face encoding
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    
    if len(encodings) == 0:
        return jsonify({"status": "error", "message": "No face detected in image"})
    
    face_encodings[name] = encodings[0]
    pd.to_pickle(face_encodings, ENCODINGS_FILE)
    
    return jsonify({"status": "success", "message": f"Face added for {name}"})

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    try:
        # Capture image from webcam
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return jsonify({"status": "error", "message": "Failed to capture image from webcam"}), 400

        # Convert image to RGB format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            return jsonify({"status": "error", "message": "No faces detected in the captured image"}), 400

        # Get face encodings
        face_encodings_list = face_recognition.face_encodings(rgb_frame, face_locations)
        if not face_encodings_list:
            return jsonify({"status": "error", "message": "Could not extract face features"}), 400

        # Recognize faces
        recognized_names = []
        for face_encoding in face_encodings_list:
            matches = face_recognition.compare_faces(
                list(face_encodings.values()), 
                face_encoding,
                tolerance=0.6
            )
            
            # Find best match
            face_distances = face_recognition.face_distance(
                list(face_encodings.values()), 
                face_encoding
            )
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index]:
                name = list(face_encodings.keys())[best_match_index]
            else:
                name = "Unknown"
            recognized_names.append(name)

        # Save attendance
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        global attendance_df
        for name in recognized_names:
            new_entry = pd.DataFrame([[name, timestamp]], columns=["Name", "Timestamp"])
            attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        
        attendance_df.to_csv(ATTENDANCE_CSV, index=False)

        return jsonify({
            "status": "success",
            "message": f"Attendance marked for: {', '.join(recognized_names)}",
            "names": recognized_names
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500
# Keep other routes the same
# Updated view_attendance() route
# @app.route("/view_attendance")
# def view_attendance():
#     return render_template("attendance.html", 
#                          tables=[attendance_df.to_html(classes='data')],
#                          titles=attendance_df.columns.values)
@app.route("/view_attendance")
def view_attendance():
    # Return styled HTML table
    return attendance_df.to_html(
        classes='table table-striped',
        index=False,
        border=0
    )

if __name__ == "__main__":
    app.run(debug=True)