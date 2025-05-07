from django.shortcuts import render
from django.http import StreamingHttpResponse,Http404
import cv2
import os
from django.shortcuts import redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import face_recognition
from django.conf import settings
import atexit
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from home.models import Person


# Cleanup resources when the application stops
def cleanup():
    video_capture.release()
    cv2.destroyAllWindows()

# atexit.register(cleanup)

# Directory to store known face images
known_faces_dir = os.path.join(settings.BASE_DIR, 'media', 'profile_picture')

video_capture = None  # Initialize as None


def get_video_capture():
    """
    Returns a valid cv2.VideoCapture object. 
    If the current video_capture is released or None, creates a new one.
    """
    global video_capture
    if video_capture is None or not video_capture.isOpened():
        video_capture = cv2.VideoCapture(0)
    return video_capture

def stop_camera(request):
    global video_capture

    # Check if video_capture is None
    if video_capture is None:
        return JsonResponse({'status': 'Camera is not initialized'})

    # Check if video capture is opened
    if video_capture.isOpened():
        video_capture.release()
        cv2.destroyAllWindows()
        return JsonResponse({'status': 'Camera stopped'})
    else:
        return JsonResponse({'status': 'Camera already stopped'})

# Load and encode known faces
def load_known_faces(known_faces_dir):
    known_face_encodings = []
    known_face_names = []

    if not os.path.exists(known_faces_dir):
        os.makedirs(known_faces_dir)  # Ensure the directory exists

    for filename in os.listdir(known_faces_dir):
        filepath = os.path.join(known_faces_dir, filename)
        print(f"Loading file: {filepath}")  # Debugging line
        try:
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)
            if encodings:  # Check if any encodings were found
                encoding = encodings[0]
                known_face_encodings.append(encoding)
                known_face_names.append(os.path.splitext(filename)[0])
                print(f"Added encoding for: {os.path.splitext(filename)[0]}")
            else:
                # pass
                print(f"No faces found in {filename}")
        except Exception as e:
            print(f"Error loading file {filepath}: {e}")
    print(f"Total known faces loaded: {len(known_face_names)}")  # Debug output
    return known_face_encodings, known_face_names

# Update the known faces list
def update_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings, known_face_names = load_known_faces(known_faces_dir)
    print(f"Known faces updated. Total encodings: {len(known_face_encodings)}")


def recognize_faces(frame, known_face_encodings, known_face_names):
    # Detect faces in the current frame
    face_locations = face_recognition.face_locations(frame, model='hog')
    print(f"Detected {len(face_locations)} face(s) in the frame.")  # Debug print

    face_encodings = face_recognition.face_encodings(frame, face_locations)
    print(f"Generated {len(face_encodings)} face encoding(s).")  # Debug print

    recognized_faces = []

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            print(f"Recognized face: {name} at location: top={top}, right={right}, bottom={bottom}, left={left}")  # Debug print
        else:
            print(f"No match found for the detected face at location: top={top}, right={right}, bottom={bottom}, left={left}")  # Debug print

        if name == "Unknown":
            recognized_faces.append((name, (left, top, right, bottom)))
        else:
            try:
                person = get_object_or_404(Person, id=name)  # Query by `name` field
                recognized_name = person.name
                print(f"Found person in database: {recognized_name}")  # Debug print
            except Http404:
                recognized_name = "Unknown"
                print(f"Person with name {name} not found in database.")  # Debug print
            recognized_faces.append((recognized_name, (left, top, right, bottom)))

    return recognized_faces



# Video stream generator for face recognition
def face_recognition_gen(known_face_encodings, known_face_names):
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Resize for faster processing
        frame = cv2.resize(frame, (640, 480))

        # Recognize faces
        recognized_faces = recognize_faces(frame, known_face_encodings, known_face_names)

        # Draw bounding boxes and labels on the frame
        for name, (left, top, right, bottom) in recognized_faces:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Encode the frame for the video stream
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

# Stream view
def stream(request):
    known_face_encodings, known_face_names = load_known_faces(known_faces_dir)
    get_video_capture()
    return StreamingHttpResponse(
        face_recognition_gen(known_face_encodings, known_face_names), 
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

# Render the face recognition page
def recognize_face(request):
    return render(request, 'recognize.html')

