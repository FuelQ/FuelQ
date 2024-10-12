import cv2
from datetime import datetime, timedelta  
import os
import firebase_admin
from firebase_admin import credentials, storage
# Firebase setup
try:
    cred = credentials.Certificate(r"E:\FuelQ\fuelq-864ff-firebase-adminsdk-uykz7-1bffd5b9e2.json")#enter your path of json file
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'fuelq-864ff.appspot.com'  
    })
    print("Firebase initialized successfully!")
except Exception as e:
    print(f"Error initializing Firebase: {e}")

bucket = storage.bucket()

def upload_to_firebase(file_path, destination_blob_name):
    """Upload an image file to Firebase Storage."""
    try:
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(file_path)
        print(f"Uploaded {file_path} to Firebase Storage as {destination_blob_name}")
    except Exception as e:
        print(f"Failed to upload {file_path}: {e}")

save_dir = r'E:\FuelQ\images' #enter your path to store images
os.makedirs(save_dir, exist_ok=True)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

start_time = datetime.now()

def get_image_files(directory):
    """Return a list of image file paths in the directory."""
    files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.png')]
    files.sort(key=os.path.getmtime)
    return files

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame!")
        break

    cv2.imshow('Live Camera', frame)
    current_time = datetime.now()

    if (current_time - start_time) >= timedelta(seconds=5):
        start_time = current_time
        timestamp_text = current_time.strftime("%I:%M:%S %p")
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color = (255, 255, 255)
        thickness = 2
        text_size, _ = cv2.getTextSize(timestamp_text, font, font_scale, thickness)
        text_w, text_h = text_size       

        position = (10, frame.shape[0] - 10)
        bottom_left = position
        top_right = (position[0] + text_w, position[1] + text_h + 10)

        cv2.rectangle(frame, (bottom_left[0], bottom_left[1] - text_h - 10), (top_right[0], bottom_left[1]), (0, 0, 0), cv2.FILLED)
        cv2.putText(frame, timestamp_text, position, font, font_scale, color, thickness, cv2.LINE_AA)

        filename = os.path.join(save_dir, f'{current_time.strftime("%H-%M-%S %d-%m-%Y")}.png')
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")

        # Upload to Firebase Storage
        upload_to_firebase(filename, f'{current_time.strftime("%H-%M-%S %d-%m-%Y")}.png')

        image_files = get_image_files(save_dir)
        if len(image_files) > 5:
            os.remove(image_files[0])
            print(f"Deleted: {image_files[0]}")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
