from flask import Flask, flash, render_template, request, jsonify, redirect, url_for, session
import os
import cv2
import subprocess
import numpy as np
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import supervision as sv
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

model = YOLO("runs/detect/train/weights/best.pt")

# Inisialisasi model Roboflow
# rf = Roboflow(api_key="W4rxsn9AtSmc8q1NWf8B")
# project = rf.workspace().project("sign-language-bisindo-qdpec")
# model = project.version(7).model

# rf = Roboflow(api_key="W4rxsn9AtSmc8q1NWf8B")
# project = rf.workspace().project("tga-bisindo")
# model = project.version(6).model

# rf = Roboflow(api_key="W4rxsn9AtSmc8q1NWf8B")
# project = rf.workspace().project("tga-bisindo")
# model = project.version(8).model

# rf = Roboflow(api_key="Gd6i46fFL6XFNzfPtlRZ")
# project = rf.workspace().project("bisindo-ng7uc")
# model = project.version(5).model

rf = Roboflow(api_key="6tIlt24dM2YYU4zpB9R4")
project = rf.workspace().project("tga-bisindo-uf0tu")
model = project.version(1).model

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
    if fps == 0:
        print("⚠ FPS tidak terdeteksi, gunakan default 25")
        fps = 25

    ext = output_path.split('.')[-1].lower()
    fourcc_map = {
        'mp4': 'mp4v',
        'avi': 'XVID',
        'webm': 'VP80',
        'mov': 'avc1'
    }
    fourcc = cv2.VideoWriter_fourcc(*fourcc_map.get(ext, 'mp4v'))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("❌ Gagal membuka VideoWriter.")
        return ""

    detected_labels = []
    written_frames = 0
    frame_count = 0
    label_annotator = sv.LabelAnnotator()
    box_annotator = sv.BoxAnnotator()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Resize untuk percepatan, tapi tetap tampilkan fullsize frame
        small_frame = cv2.resize(frame, (640, 360))

        if frame_count % 2 == 0:  # skip setiap 2 frame
            out.write(frame)
            written_frames += 1
            continue

        result = model.predict(small_frame, confidence=40, overlap=30).json()
        boxes = []
        confidences = []
        class_ids = []
        labels = []

        if 'predictions' in result and len(result['predictions']) > 0:
            for prediction in result['predictions']:
                confidence = float(prediction['confidence'])
                if confidence < 0.7:
                    continue

                # Koordinat pada small_frame (640x360), perlu scaling ke ukuran asli
                scale_x = width / 640
                scale_y = height / 360

                x_center = prediction['x'] * scale_x
                y_center = prediction['y'] * scale_y
                box_width = prediction['width'] * scale_x
                box_height = prediction['height'] * scale_y

                x1 = int(x_center - box_width / 2)
                y1 = int(y_center - box_height / 2)
                x2 = int(x_center + box_width / 2)
                y2 = int(y_center + box_height / 2)

                class_label = prediction['class']
                label_text = f"{class_label} {confidence:.2f}"

                boxes.append([x1, y1, x2, y2])
                confidences.append(confidence)
                class_ids.append(prediction.get('class_id', 0))
                labels.append(label_text)

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
            written_frames += 1

            for class_label in set([label.split()[0] for label in labels]):
                detected_labels.append(class_label)
        else:
            out.write(frame)
            written_frames += 1

    cap.release()
    out.release()

    if written_frames == 0 or not os.path.exists(output_path):
        print("❌ Tidak ada frame yang ditulis.")
        return ""

    # Konversi FFmpeg
    temp_output_path = output_path.replace(f".{ext}", f"_temp.{ext}")
    ffmpeg_command = [
        "D:\\app\\ffmpeg\\ffmpeg-2025-02-13-git-19a2d26177-full_build\\bin\\ffmpeg.exe", "-y",
        "-i", output_path,
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        temp_output_path.replace("\\", "/")
    ]

    try:
        subprocess.run(ffmpeg_command, check=True)
        os.remove(output_path)
        os.rename(temp_output_path, output_path)
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e}")

    unique_labels = list(dict.fromkeys(detected_labels))
    label_sentence = " ".join(unique_labels)
    print(label_sentence)
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
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         confirm = request.form['confirm_password']

#     if len(username) > 20:
#         return "Username terlalu panjang (maks 20 karakter)", 400

#     if len(password) > 20:
#         return "Password terlalu panjang (maks 20 karakter)", 400

#     if password != confirm:
#         flash("Password tidak cocok.")
#         return render_template('register.html')

#     conn = get_db_connection()
#     try:
#         conn.execute(
#             "INSERT INTO users (username, password) VALUES (?, ?)",
#             (username, password)
#         )
#         conn.commit()
#     except sqlite3.IntegrityError:
#             flash("Username sudah digunakan.")
#             return render_template('register.html')
#     finally:
#             conn.close()

#     return redirect(url_for('login'))
    
#     return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']

        if len(username) > 20:
            return "Username terlalu panjang (maks 20 karakter)", 400

        if len(password) > 20:
            return "Password terlalu panjang (maks 20 karakter)", 400

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
    
    # Jika GET, langsung tampilkan halaman tanpa validasi
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