# from flask import Flask, render_template, request, jsonify
# import os
# import cv2
# import subprocess
# import json
# from werkzeug.utils import secure_filename
# from ultralytics import YOLO

# app = Flask(__name__)
# UPLOAD_FOLDER_INDEX = "static/uploads/index"
# UPLOAD_FOLDER_DATASET = "static/uploads/dataset"
# PROCESSED_FOLDER = "static/results"
# ANNOTATION_FILE = 'annotations.json'
# ALLOWED_EXTENSIONS = {'mp4', 'avi', 'webm'}

# os.makedirs(UPLOAD_FOLDER_INDEX, exist_ok=True)
# os.makedirs(UPLOAD_FOLDER_DATASET, exist_ok=True)
# os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# app.config['UPLOAD_FOLDER_DATASET'] = UPLOAD_FOLDER_DATASET
# model = YOLO("runs/detect/train/weights/best.pt")

# # Cek ekstensi file
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# # Load anotasi jika ada
# if os.path.exists(ANNOTATION_FILE):
#     with open(ANNOTATION_FILE, 'r') as f:
#         annotations = json.load(f)
# else:
#     annotations = {}

# @app.route('/upload', methods=['GET', 'POST'])
# def upload_page():
#     if request.method == 'GET':
#         return render_template('upload.html')

#     if 'file' not in request.files or 'label' not in request.form:
#         return jsonify({'error': 'File dan label harus diisi!'}), 400

#     file = request.files['file']
#     label = request.form['label']

#     if file.filename == '':
#         return jsonify({'error': 'Nama file tidak valid!'}), 400

#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER_DATASET'], filename)
#         file.save(filepath)

#         # Simpan anotasi
#         annotations[filename] = label
#         with open(ANNOTATION_FILE, 'w') as f:
#             json.dump(annotations, f, indent=4)

#         return jsonify({'message': 'File berhasil diunggah!', 'filename': filename, 'label': label}), 200
#     else:
#         return jsonify({'error': 'Jenis file tidak diizinkan!'}), 400


# # API untuk mendapatkan daftar dataset
# @app.route('/dataset', methods=['GET'])
# def get_dataset():
#     return jsonify(annotations)

# # Endpoint Train
# @app.route("/train", methods=["POST"])
# def train_model():
#     data = request.get_json()
#     epochs = int(data.get("epochs", 50))
#     batch_size = int(data.get("batchSize", 16))

#     try:
#         model = YOLO("yolov8n.pt")  # Gunakan model YOLOv8
#         results = model.train(data="data.yaml", epochs=epochs, batch=batch_size)

#         return jsonify({"success": True, "message": "Pelatihan selesai!"})
#     except Exception as e:
#         return jsonify({"success": False, "message": f"Error: {str(e)}"})

# @app.route('/train')
# def train_page():
#     return render_template('train.html')

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         file = request.files["video"]
#         if file:
#             file_path = os.path.join(UPLOAD_FOLDER_INDEX, file.filename)
#             file.save(file_path)

#             output_path = os.path.join(PROCESSED_FOLDER, "processed_" + file.filename)
#             detected_labels = process_video(file_path, output_path)

#             return jsonify({"video_path": f"/{output_path}", "detected_labels": detected_labels})

#     return render_template("index.html", uploaded=False)

# def process_video(input_path, output_path):
#     cap = cv2.VideoCapture(input_path)
#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     fps = int(cap.get(cv2.CAP_PROP_FPS))

#     # Tentukan kodek berdasarkan ekstensi file output
#     ext = output_path.split('.')[-1].lower()
#     fourcc_map = {
#         'mp4': 'mp4v',  # MP4
#         'avi': 'XVID',  # AVI
#         'webm': 'VP80', # WebM
#         'mov': 'avc1'   # MOV
#     }

#     fourcc = cv2.VideoWriter_fourcc(*fourcc_map.get(ext, 'mp4v'))
#     out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#     detected_labels = []

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # 🔥 Deteksi bahasa isyarat menggunakan YOLOv8 yang sudah dilatih
#         frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = model(frame_rgb)

#         for result in results:
#             for box in result.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 label = model.names[int(box.cls)]
#                 conf = float(box.conf)

#                 # Simpan label yang terdeteksi
#                 detected_labels.append(label)

#                 # Gambar kotak deteksi
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.putText(frame, f"{label} ({conf:.2f})", (x1, y1 - 10), 
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#         out.write(frame)

#     cap.release()
#     out.release()

#     # 🔄 Konversi dengan FFmpeg untuk kompatibilitas
#     temp_output_path = output_path.replace(f".{ext}", f"_temp.{ext}")
#     ffmpeg_command = [
#         "D:\\app\\ffmpeg\\ffmpeg-2025-02-13-git-19a2d26177-full_build\\bin\\ffmpeg.exe", "-y",
#         "-i", output_path, "-c:v", "libx264", "-preset", "fast",
#         "-c:a", "aac", "-b:a", "128k", temp_output_path
#     ]
    
#     try:
#         subprocess.run(ffmpeg_command, check=True)
#         os.remove(output_path)
#         os.rename(temp_output_path, output_path)
#     except subprocess.CalledProcessError as e:
#         print(f"Terjadi kesalahan dalam konversi: {e}")

#     return detected_labels  # Kembalikan daftar label yang terdeteksi

# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, flash, render_template, request, jsonify, redirect, url_for, session
import os
import cv2
import subprocess
import numpy as np
from werkzeug.utils import secure_filename
from roboflow import Roboflow
import supervision as sv
from database import get_user
import sqlite3
from datetime import timedelta
from database import simpan_riwayat

app = Flask(__name__)
UPLOAD_FOLDER_INDEX = "static/uploads/index"
UPLOAD_FOLDER = "static/uploads"
PROCESSED_FOLDER = "static/results"
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'webm'}

os.makedirs(UPLOAD_FOLDER_INDEX, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Inisialisasi model Roboflow
rf = Roboflow(api_key="W4rxsn9AtSmc8q1NWf8B")
project = rf.workspace().project("sign-language-bisindo-qdpec")
model = project.version(7).model

# rf = Roboflow(api_key="W4rxsn9AtSmc8q1NWf8B")
# project = rf.workspace().project("tga-bisindo")
# model = project.version(6).model

# Cek ekstensi file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file found'})

        file = request.files['video']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'})

        filename = secure_filename(file.filename)
        video_path = os.path.join('uploads', filename)
        output_filename = f"processed_{filename}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)

        file.save(video_path)

        # 🔹 Proses video & ambil label
        hasil_deteksi = process_video(video_path, output_path)

        return jsonify({
            'success': True,
            'video_url': url_for('static', filename=f"results/{output_filename}"),
            'hasil': hasil_deteksi
        })

    return render_template('index.html')

def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    ext = output_path.split('.')[-1].lower()
    fourcc_map = {
        'mp4': 'mp4v',
        'avi': 'XVID',
        'webm': 'VP80',
        'mov': 'avc1'
    }
    fourcc = cv2.VideoWriter_fourcc(*fourcc_map.get(ext, 'mp4v'))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    detected_labels = []
    label_annotator = sv.LabelAnnotator()
    box_annotator = sv.BoxAnnotator()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        result = model.predict(frame, confidence=40, overlap=30).json()

        boxes = []
        confidences = []
        class_ids = []
        labels = []

        if 'predictions' in result and len(result['predictions']) > 0:
            for prediction in result['predictions']:
                confidence = float(prediction['confidence'])
                if confidence < 0.7:  # Hanya ambil confidence > 78%
                    continue

                x_center = prediction['x']
                y_center = prediction['y']
                box_width = prediction['width']
                box_height = prediction['height']

                x1 = int(x_center - box_width / 2)
                y1 = int(y_center - box_height / 2)
                x2 = int(x_center + box_width / 2)
                y2 = int(y_center + box_height / 2)

                class_label = prediction['class']
                label_text = f"{class_label} {confidence:.1f}"

                boxes.append([x1, y1, x2, y2])
                confidences.append(confidence)
                class_ids.append(prediction.get('class_id', 0))
                labels.append(label_text)
                detected_labels.append(class_label)

        # Jika ada deteksi valid
        if boxes:
            boxes_array = np.array(boxes, dtype=np.float32)
            confidences_array = np.array(confidences, dtype=np.float32)
            class_ids_array = np.array(class_ids, dtype=int)

            detections = sv.Detections(
                xyxy=boxes_array,
                confidence=confidences_array,
                class_id=class_ids_array
            )

            annotated_frame = box_annotator.annotate(
                scene=frame, detections=detections)
            annotated_frame = label_annotator.annotate(
                scene=annotated_frame, detections=detections, labels=labels)

            out.write(annotated_frame)
        else:
            # Jika tidak ada deteksi valid, tulis frame apa adanya
            out.write(frame)

    cap.release()
    out.release()

    # 🔁 Konversi dengan FFmpeg
    temp_output_path = output_path.replace(f".{ext}", f"_temp.{ext}")
    ffmpeg_command = [
        "D:\\app\\ffmpeg\\ffmpeg-2025-02-13-git-19a2d26177-full_build\\bin\\ffmpeg.exe", "-y",
        "-i", output_path, "-c:v", "libx264", "-preset", "fast",
        "-c:a", "aac", "-b:a", "128k", temp_output_path.replace("\\", "/")
    ]
    
    try:
        subprocess.run(ffmpeg_command, check=True)
        os.remove(output_path)
        os.rename(temp_output_path, output_path)
    except subprocess.CalledProcessError as e:
        print(f"Terjadi kesalahan dalam konversi: {e}")

    # Hanya ambil label unik dengan urutan berdasarkan kemunculan
    seen = set()
    unique_labels = [label for label in detected_labels if not (label in seen or seen.add(label))]

    label_sentence = " ".join(unique_labels)
    print("Label terdeteksi:", label_sentence)
    return label_sentence

app.permanent_session_lifetime = timedelta(days=7)  # Bisa diubah sesuai kebutuhan
app.secret_key = 'sayaPunyaProyekBISINDO2025'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')  # Ambil nilai dari form

        user = get_user(username)
        if user:
            if password == user[2]:  # Bandingkan password langsung (plaintext)
                session['username'] = username
                session.permanent = bool(remember)  # Aktifkan "remember me" jika dicentang
                return redirect(url_for('dashboard'))
            else:
                error = 'Password salah'
        else:
            error = 'User tidak ditemukan'
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if password != confirm:
            flash("Password tidak cocok.")
            return render_template('register.html')

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username sudah digunakan.")
            return render_template('register.html')
        finally:
            conn.close()

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'video' not in request.files:
            return jsonify({'success': False, 'error': 'No video file found'})

        file = request.files['video']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'})

        filename = secure_filename(file.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
        output_filename = f"processed_{filename}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename).replace("\\", "/")

        file.save(video_path)

        # 🔹 Proses video & ambil label
        hasil_deteksi = process_video(video_path, output_path)
        if 'username' in session:
            simpan_riwayat(session['username'], video_path, output_path, hasil_deteksi, filename)


        return jsonify({
            'success': True,
            'video_url': url_for('static', filename=output_path.split("static/")[-1]),
            'hasil': hasil_deteksi
        })

    return render_template('dashboard.html')

@app.route('/riwayat')
def riwayat():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    history = conn.execute(
        "SELECT * FROM history WHERE username = ? ORDER BY created_at DESC",
        (session['username'],)
    ).fetchall()
    conn.close()

    return render_template('riwayat.html', history=history)

@app.route('/hapus_riwayat/<int:id>', methods=['POST'])
def hapus_riwayat(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM history WHERE id = ? AND username = ?", (id, session['username']))
    conn.commit()
    conn.close()
    return redirect(url_for('riwayat'))

@app.route('/logout')
def logout():
    session.clear()  # Menghapus semua data session
    return redirect(url_for('index'))  # Kembali ke halaman login

if __name__ == "__main__":
    app.run(debug=True)