# Camp Tutor Student Management System
# Raspberry Pi 3B+ Optimized

import os
import sys
import time
import json
import logging
import threading
import subprocess
import signal
from pathlib import Path
from datetime import datetime

# Base directories - relative to pi folder
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STUDENTS_DIR = DATA_DIR / "students"
MODELS_DIR = BASE_DIR / "models"
CONFIG_FILE = DATA_DIR / "config.json"

# Settings
PICAMERA_RESOLUTION = (640, 480)
FACIAL_RECOGNITION_THRESHOLD = 0.6
MIN_FACE_SIZE = (80, 80)
SERVER_PORT = 5000
OFFLINE_MODE_DEFAULT = True

# WiFi config path
WIFI_CONFIG = DATA_DIR / "wifi.json"

# Logging setup
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'camp_tutor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages system configuration."""
    
    def __init__(self):
        self.config = {}
        self._load()
    
    def _load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    self.config = json.load(f)
            except Exception as e:
                logger.error(f"Config load error: {e}")
                self.config = self._default_config()
        else:
            self.config = self._default_config()
    
    def _default_config(self):
        return {
            "offline_mode": OFFLINE_MODE_DEFAULT,
            "server_port": SERVER_PORT,
            "language": "en",
            "focused_mode": False,
            "wake_word": "camp tutor",
            " inactivity_timeout": 300,
            "face_recognition_threshold": FACIAL_RECOGNITION_THRESHOLD,
            "classrooms": {}
        }
    
    def save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()
    
    def get_classrooms(self):
        return self.config.get("classrooms", {})
    
    def add_classroom(self, name, student_ids):
        classrooms = self.get_classrooms()
        classrooms[name] = student_ids
        self.config["classrooms"] = classrooms
        self.save()
    
    def remove_classroom(self, name):
        classrooms = self.get_classrooms()
        if name in classrooms:
            del classrooms[name]
            self.config["classrooms"] = classrooms
            self.save()


class WiFiManager:
    """Manages WiFi connectivity."""
    
    def __init__(self):
        self.connected = False
        self.current_ssid = None
        self._load_credentials()
    
    def _load_credentials(self):
        if WIFI_CONFIG.exists():
            try:
                with open(WIFI_CONFIG) as f:
                    creds = json.load(f)
                    self.saved_ssid = creds.get("ssid", "")
                    self.saved_password = creds.get("password", "")
            except Exception:
                self.saved_ssid = ""
                self.saved_password = ""
        else:
            self.saved_ssid = ""
            self.saved_password = ""
    
    def save_credentials(self, ssid, password):
        """Save WiFi credentials persistently."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(WIFI_CONFIG, 'w') as f:
            json.dump({"ssid": ssid, "password": password}, f)
        self.saved_ssid = ssid
        self.saved_password = password
        logger.info(f"WiFi credentials saved for: {ssid}")
    
    def has_saved_network(self):
        return bool(self.saved_ssid)
    
    def connect(self, ssid=None, password=None):
        """Connect to WiFi network."""
        target_ssid = ssid or self.saved_ssid
        target_password = password or self.saved_password
        
        if not target_ssid or not target_password:
            return False
        
        try:
            result = subprocess.run(
                ["nmcli", "device", "wifi", "connect", target_ssid, "password", target_password],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.connected = True
                self.current_ssid = target_ssid
                logger.info(f"Connected to WiFi: {target_ssid}")
                return True
            else:
                logger.warning(f"WiFi connection failed: {result.stderr.decode()}")
                return False
                
        except FileNotFoundError:
            logger.warning("nmcli not available")
            return False
        except Exception as e:
            logger.error(f"WiFi connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WiFi."""
        try:
            subprocess.run(["nmcli", "device", "disconnect", "wlan0"], capture_output=True)
            self.connected = False
            self.current_ssid = None
        except Exception as e:
            logger.error(f"WiFi disconnect error: {e}")
    
    def get_status(self):
        """Get WiFi status."""
        return {
            "connected": self.connected,
            "ssid": self.current_ssid,
            "has_saved": self.has_saved_network()
        }
    
    def scan_networks(self):
        """Scan for available networks."""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"],
                capture_output=True,
                timeout=15
            )
            if result.returncode == 0:
                networks = result.stdout.decode().strip().split('\n')
                return [n for n in networks if n]
        except Exception:
            pass
        return []


class StudentDatabase:
    """Manages student data with photos."""
    
    def __init__(self):
        STUDENTS_DIR.mkdir(parents=True, exist_ok=True)
        self.students = {}
        self._load_index()
    
    def _load_index(self):
        index_file = STUDENTS_DIR / "index.json"
        if index_file.exists():
            try:
                with open(index_file) as f:
                    self.students = json.load(f)
            except Exception as e:
                logger.error(f"Index load error: {e}")
    
    def _save_index(self):
        with open(STUDENTS_DIR / "index.json", 'w') as f:
            json.dump(self.students, f, indent=2)
    
    def add_student(self, student_id, name, classroom=None):
        """Add new student."""
        student_dir = STUDENTS_DIR / student_id
        student_dir.mkdir(parents=True, exist_ok=True)
        
        self.students[student_id] = {
            "id": student_id,
            "name": name,
            "classroom": classroom,
            "created_at": datetime.now().isoformat(),
            "photo_count": 0,
            "last_seen": None,
            "session_count": 0
        }
        
        self._save_index()
        logger.info(f"Added student: {student_id} - {name}")
        return student_id
    
    def get_student(self, student_id):
        return self.students.get(student_id)
    
    def get_all_students(self):
        return list(self.students.values())
    
    def update_student(self, student_id, data):
        if student_id in self.students:
            self.students[student_id].update(data)
            self._save_index()
            return True
        return False
    
    def delete_student(self, student_id):
        if student_id in self.students:
            student_dir = STUDENTS_DIR / student_id
            if student_dir.exists():
                import shutil
                shutil.rmtree(student_dir)
            del self.students[student_id]
            self._save_index()
            return True
        return False
    
    def save_photo(self, student_id, photo_data, filename=None):
        """Save student photo."""
        student_dir = STUDENTS_DIR / student_id
        student_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            count = self.students.get(student_id, {}).get("photo_count", 0)
            filename = f"photo_{count + 1}.jpg"
        
        filepath = student_dir / filename
        with open(filepath, 'wb') as f:
            f.write(photo_data)
        
        if student_id in self.students:
            self.students[student_id]["photo_count"] = (
                self.students[student_id].get("photo_count", 0) + 1
            )
            self._save_index()
        
        return str(filepath)
    
    def get_photo_path(self, student_id, photo_index=1):
        filepath = STUDENTS_DIR / student_id / f"photo_{photo_index}.jpg"
        return str(filepath) if filepath.exists() else None
    
    def get_classroom_students(self, classroom):
        return [s for s in self.students.values() if s.get("classroom") == classroom]
    
    def record_session(self, student_id):
        if student_id in self.students:
            self.students[student_id]["session_count"] = (
                self.students[student_id].get("session_count", 0) + 1
            )
            self.students[student_id]["last_seen"] = datetime.now().isoformat()
            self._save_index()


class FacialRecognition:
    """Optimized facial recognition for Pi 3B+."""
    
    def __init__(self):
        self.face_recognizer = None
        self.face_cascade = None
        self._initialized = False
    
    def initialize(self):
        """Initialize facial recognition."""
        if self._initialized:
            return True
        
        try:
            import cv2
            import numpy as np
            
            # Load Haar cascade for face detection
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if not self.face_cascade.empty():
                # Try to load LBPH recognizer
                MODEL_PATH = MODELS_DIR / "face_model.yml"
                if MODEL_PATH.exists():
                    self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
                    self.face_recognizer.read(str(MODEL_PATH))
                
                self._initialized = True
                logger.info("Facial recognition initialized")
                return True
            else:
                logger.error("Face cascade failed to load")
                return False
                
        except ImportError as e:
            logger.error(f"OpenCV not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Facial recognition init error: {e}")
            return False
    
    def detect_faces(self, image):
        """Detect faces in image."""
        if not self._initialized:
            return []
        
        try:
            import cv2
            import numpy as np
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=MIN_FACE_SIZE
            )
            
            return faces
            
        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []
    
    def recognize_face(self, face_image):
        """Recognize a face."""
        if not self._initialized or self.face_recognizer is None:
            return None, 0.0
        
        try:
            import cv2
            import numpy as np
            
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            label, confidence = self.face_recognizer.predict(gray)
            
            if confidence < FACIAL_RECOGNITION_THRESHOLD * 100:
                return str(label), confidence / 100.0
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"Face recognition error: {e}")
            return None, 0.0
    
    def train_model(self, student_ids):
        """Train face recognition model."""
        try:
            import cv2
            import numpy as np
            from PIL import Image
            
            images = []
            labels = []
            
            for student_id in student_ids:
                student_dir = STUDENTS_DIR / student_id
                if not student_dir.exists():
                    continue
                
                for photo_file in student_dir.glob("photo_*.jpg"):
                    try:
                        img = Image.open(photo_file).convert('L')
                        img = img.resize((100, 100))
                        images.append(np.array(img))
                        labels.append(int(student_id.split('_')[-1]))
                    except Exception:
                        continue
            
            if len(images) < 2:
                logger.warning("Not enough images to train model")
                return False
            
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(images, np.array(labels))
            
            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            recognizer.save(str(MODELS_DIR / "face_model.yml"))
            
            self.face_recognizer = recognizer
            logger.info("Face model trained successfully")
            return True
            
        except Exception as e:
            logger.error(f"Model training error: {e}")
            return False


class CameraCapture:
    """Pi Camera capture optimized for Pi 3B+."""
    
    def __init__(self):
        self.camera = None
        self._initialized = False
    
    def initialize(self):
        if self._initialized:
            return True
        
        try:
            from picamera2 import Picamera2
            
            self.camera = Picamera2()
            config = self.camera.create_still_configuration()
            self.camera.configure(config)
            
            self._initialized = True
            logger.info("Camera initialized")
            return True
            
        except ImportError:
            try:
                from picamera import Camera
                self.camera = Camera()
                self._initialized = True
                return True
            except Exception as e:
                logger.error(f"Camera init error: {e}")
                return False
        except Exception as e:
            logger.error(f"Camera init error: {e}")
            return False
    
    def capture_frame(self):
        """Capture a single frame."""
        if not self._initialized:
            return None
        
        try:
            from picamera2 import Picamera2
            import libcamera
            
            if hasattr(self.camera, 'capture_array'):
                return self.camera.capture_array()
            
        except Exception as e:
            logger.error(f"Capture error: {e}")
        
        return None
    
    def capture_image(self, filepath):
        """Capture image to file."""
        if not self._initialized or not self.camera:
            return False
        
        try:
            self.camera.capture_file(filepath)
            return True
        except Exception as e:
            logger.error(f"Capture error: {e}")
            return False
    
    def close(self):
        if self.camera:
            self.camera.close()
            self.camera = None
            self._initialized = False


class WebServer:
    """Flask web server for mobile access."""
    
    def __init__(self, student_db, config, wifi_manager, facial_rec):
        self.student_db = student_db
        self.config = config
        self.wifi_manager = wifi_manager
        self.facial_rec = facial_rec
        self.app = None
        self._setup_routes()
    
    def _setup_routes(self):
        from flask import Flask, render_template_string, request, jsonify, send_from_directory
        import io
        
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        
        # HTML templates
        self.base_html = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Camp Tutor</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              background: #1a1a2e; color: #eee; min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        h1 { color: #00d9ff; text-align: center; margin-bottom: 20px; }
        .nav { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; }
        .nav a { flex: 1; min-width: 100px; padding: 12px; background: #16213e;
                 color: #00d9ff; text-decoration: none; text-align: center;
                 border-radius: 8px; transition: background 0.3s; }
        .nav a:hover, .nav a.active { background: #0f3460; }
        .card { background: #16213e; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; color: #aaa; }
        .form-group input, .form-group select { width: 100%; padding: 12px;
                 background: #1a1a2e; border: 1px solid #0f3460; color: #eee;
                 border-radius: 6px; font-size: 16px; }
        button, .btn { padding: 12px 24px; background: #00d9ff; color: #1a1a2e;
                    border: none; border-radius: 6px; cursor: pointer;
                    font-size: 16px; font-weight: bold; transition: opacity 0.3s; }
        button:hover, .btn:hover { opacity: 0.8; }
        .btn-danger { background: #ff4757; color: white; }
        .btn-small { padding: 8px 16px; font-size: 14px; }
        .student-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                    gap: 15px; }
        .student-card { background: #0f3460; border-radius: 8px; padding: 15px; text-align: center; }
        .student-card img { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; margin-bottom: 10px; }
        .status { padding: 10px; background: #0f3460; border-radius: 6px; margin-bottom: 20px; }
        .status.online { border-left: 4px solid #00ff00; }
        .status.offline { border-left: 4px solid #ff4757; }
        .flash { padding: 10px; background: #0f3460; border-radius: 6px; margin-bottom: 10px; }
        .capture-area { text-align: center; padding: 20px; }
        #video-preview { width: 100%; max-width: 400px; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Camp Tutor</h1>
        
        <div class="nav">
            <a href="/">Students</a>
            <a href="/add">Add Student</a>
            <a href="/wifi">WiFi</a>
            <a href="/settings">Settings</a>
        </div>
        
        {% if status %}
        <div class="status {{ 'online' if status.connected else 'offline' }}">
            WiFi: {{ status.ssid if status.connected else 'Not connected' }}
        </div>
        {% endif %}
        
        {% for message in get_flashed_messages() %}
        <div class="flash">{{ message }}</div>
        {% endfor %}
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""
        
        self.students_html = """
{% extends "base" %}
{% block content %}
<div class="card">
    <h2>Registered Students ({{ students|length }})</h2>
</div>

<div class="student-grid">
{% for student in students %}
    <div class="student-card">
        {% if student.photo_count > 0 %}
        <img src="/photo/{{ student.id }}/1" alt="{{ student.name }}">
        {% else %}
        <img src="/static/default_avatar.png" alt="No photo">
        {% endif %}
        <div><strong>{{ student.name }}</strong></div>
        <div style="color: #888; font-size: 12px;">
            Class: {{ student.classroom or 'None' }}<br>
            Sessions: {{ student.session_count }}
        </div>
        <div style="margin-top: 10px;">
            <a href="/edit/{{ student.id }}" class="btn btn-small">Edit</a>
        </div>
    </div>
{% endfor %}
</div>
{% endblock %}
"""
        
        self.add_student_html = """
{% extends "base" %}
{% block content %}
<div class="card">
    <h2>Add New Student</h2>
    <form method="POST" enctype="multipart/form-data">
        <div class="form-group">
            <label>Student Name</label>
            <input type="text" name="name" required placeholder="Enter name">
        </div>
        
        <div class="form-group">
            <label>Classroom</label>
            <select name="classroom">
                <option value="">No classroom</option>
                {% for classroom in classrooms %}
                <option value="{{ classroom }}">{{ classroom }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label>Add Photo</label>
            <input type="file" name="photo" accept="image/*" required>
            <p style="color: #888; font-size: 12px; margin-top: 5px;">
                Take a photo using your mobile device and upload here.
            </p>
        </div>
        
        <div class="capture-area">
            <p>Or use camera:</p>
            <video id="video-preview" autoplay playsinline></video>
            <canvas id="canvas" style="display:none;"></canvas>
            <button type="button" onclick="capturePhoto()" class="btn">Capture Photo</button>
        </div>
        
        <button type="submit" class="btn">Add Student</button>
    </form>
</div>

<script>
async function capturePhoto() {
    const video = document.getElementById('video-preview');
    const canvas = document.getElementById('canvas');
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    stream.getTracks().forEach(track => track.stop());
    
    const dataURL = canvas.toDataURL('image/jpeg');
    const formData = new FormData();
    formData.append('photo', dataURL);
    formData.append('name', document.querySelector('input[name="name"]').value);
    formData.append('classroom', document.querySelector('select[name="classroom"]').value);
    
    fetch('/capture_photo', {
        method: 'POST',
        body: formData
    }).then(r => window.location.href = '/');
}
</script>
{% endblock %}
"""
        
        self.wifi_html = """
{% extends "base" %}
{% block content %}
<div class="card">
    <h2>WiFi Settings</h2>
    
    <form method="POST">
        <div class="form-group">
            <label>Network Name (SSID)</label>
            <input type="text" name="ssid" value="{{ saved_ssid }}" placeholder="Enter WiFi name">
        </div>
        
        <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" value="{{ saved_password }}" placeholder="Enter password">
        </div>
        
        <button type="submit" class="btn">Save & Connect</button>
    </form>
    
    <h3 style="margin-top: 20px;">Available Networks</h3>
    <div style="margin-top: 10px;">
        {% for network in networks %}
        <div style="padding: 8px; background: #0f3460; margin-bottom: 5px; border-radius: 4px;">
            {{ network }}
        </div>
        {% endfor %}
    </div>
</div>

<div class="card">
    <h3>Connection Mode</h3>
    <form method="POST" action="/mode">
        <div class="form-group">
            <label>
                <input type="checkbox" name="offline_mode" {% if offline_mode %}checked{% endif %}
                Offline Mode (teaching mode)
            </label>
            <p style="color: #888; font-size: 12px;">
                When offline, AI focuses on teaching without cloud features.
            </p>
        </div>
        
        <button type="submit" class="btn">Save Mode</button>
    </form>
</div>
{% endblock %}
"""
        
        self.edit_student_html = """
{% extends "base" %}
{% block content %}
<div class="card">
    <h2>Edit Student: {{ student.name }}</h2>
    
    <form method="POST">
        <div class="form-group">
            <label>Name</label>
            <input type="text" name="name" value="{{ student.name }}" required>
        </div>
        
        <div class="form-group">
            <label>Classroom</label>
            <select name="classroom">
                <option value="">No classroom</option>
                {% for classroom in classrooms %}
                <option value="{{ classroom }}" {% if student.classroom == classroom %}selected{% endif %}>
                    {{ classroom }}
                </option>
                {% endfor %}
            </select>
        </div>
        
        <button type="submit" class="btn">Save Changes</button>
    </form>
    
    <h3 style="margin-top: 20px;">Photos</h3>
    <div class="student-grid">
        {% for i in range(1, student.photo_count + 1) %}
        <div>
            <img src="/photo/{{ student.id }}/{{ i }}" style="width: 80px; height: 80px; border-radius: 50%;">
        </div>
        {% endfor %}
    </div>
    
    <h3 style="margin-top: 20px;">Add More Photos</h3>
    <form method="POST" enctype="multipart/form-data" action="/photo/{{ student.id }}/add">
        <div class="form-group">
            <input type="file" name="photo" accept="image/*" required>
        </div>
        <button type="submit" class="btn">Add Photo</button>
    </form>
    
    <div style="margin-top: 30px;">
        <form method="POST" action="/delete/{{ student.id }}">
            <button type="submit" class="btn btn-danger" onclick="return confirm('Delete student?')">
                Delete Student
            </button>
        </form>
    </div>
</div>
{% endblock %}
"""
        
        self.settings_html = """
{% extends "base" %}
{% block content %}
<div class="card">
    <h2>Settings</h2>
    
    <h3>Classes</h3>
    <form method="POST" action="/classroom/add">
        <div class="form-group">
            <input type="text" name="classroom" placeholder="New classroom name">
            <button type="submit" class="btn btn-small">Add Classroom</button>
        </div>
    </form>
    
    <ul>
        {% for classroom in classrooms %}
        <li>{{ classroom }}</li>
        {% endfor %}
    </ul>
</div>

<div class="card">
    <h3>Training</h3>
    <form method="POST" action="/train">
        <button type="submit" class="btn">Retrain Face Model</button>
    </form>
</div>

<div class="card">
    <h3>System Info</h3>
    <p>Mode: {{ 'Offline' if offline_mode else 'Online (Focused)' }}</p>
    <p>Students: {{ student_count }}</p>
</div>
{% endblock %}
"""
        
        # Route handlers
        @self.app.route('/')
        def index():
            from flask import render_template_string, flash
            students = self.student_db.get_all_students()
            status = self.wifi_manager.get_status()
            return render_template_string(
                self.base_html + self.students_html,
                students=students,
                status=status
            )
        
        @self.app.route('/add', methods=['GET', 'POST'])
        def add_student():
            from flask import render_template_string, flash, redirect, url_for
            classrooms = self.config.get_classrooms()
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                classroom = request.form.get('classroom', '').strip()
                
                if name:
                    student_id = f"student_{int(time.time())}"
                    self.student_db.add_student(student_id, name, classroom or None)
                    
                    # Handle photo upload
                    photo = request.files.get('photo')
                    if photo and photo.filename:
                        import uuid
                        self.student_db.save_photo(student_id, photo.read(), f"photo_{uuid.uuid4().hex[:8]}.jpg")
                    
                    flash(f"Student {name} added!")
                    return redirect(url_for('index'))
            
            return render_template_string(
                self.base_html + self.add_student_html,
                classrooms=list(classrooms.keys())
            )
        
        @self.app.route('/capture_photo', methods=['POST'])
        def capture_photo():
            from flask import request, redirect, url_for, flash
            import uuid
            
            name = request.form.get('name', '').strip()
            classroom = request.form.get('classroom', '').strip()
            
            if name:
                student_id = f"student_{int(time.time())}"
                self.student_db.add_student(student_id, name, classroom or None)
                
                # Handle data URL
                photo_data = request.form.get('photo')
                if photo_data and photo_data.startswith('data:'):
                    import base64
                    header, data = photo_data.split(',', 1)
                    photo_bytes = base64.b64decode(data)
                    self.student_db.save_photo(student_id, photo_bytes)
                
                flash(f"Photo captured for {name}!")
            
            return redirect(url_for('index'))
        
        @self.app.route('/photo/<student_id>/<int:index>')
        def get_photo(student_id, index):
            from flask import send_file
            path = self.student_db.get_photo_path(student_id, index)
            if path and os.path.exists(path):
                return send_file(path, mimetype='image/jpeg')
            return send_file(str(BASE_DIR / "static" / "default_avatar.png"), mimetype='image/png')
        
        @self.app.route('/edit/<student_id>', methods=['GET', 'POST'])
        def edit_student(student_id):
            from flask import render_template_string, redirect, url_for, flash
            student = self.student_db.get_student(student_id)
            if not student:
                return redirect(url_for('index'))
            
            classrooms = self.config.get_classrooms()
            
            if request.method == 'POST':
                name = request.form.get('name', '').strip()
                classroom = request.form.get('classroom', '').strip()
                
                self.student_db.update_student(student_id, {
                    'name': name,
                    'classroom': classroom or None
                })
                flash("Student updated!")
                return redirect(url_for('index'))
            
            return render_template_string(
                self.base_html + self.edit_student_html,
                student=student,
                classrooms=classrooms
            )
        
        @self.app.route('/photo/<student_id>/add', methods=['POST'])
        def add_photo(student_id):
            from flask import redirect, url_for, flash
            photo = request.files.get('photo')
            if photo and photo.filename:
                import uuid
                self.student_db.save_photo(student_id, photo.read(), f"photo_{uuid.uuid4().hex[:8]}.jpg")
                flash("Photo added!")
            return redirect(url_for('edit_student', student_id=student_id))
        
        @self.app.route('/delete/<student_id>', methods=['POST'])
        def delete_student(student_id):
            from flask import redirect, url_for, flash
            self.student_db.delete_student(student_id)
            flash("Student deleted!")
            return redirect(url_for('index'))
        
        @self.app.route('/wifi', methods=['GET', 'POST'])
        def wifi_settings():
            from flask import render_template_string
            status = self.wifi_manager.get_status()
            networks = self.wifi_manager.scan_networks()
            classrooms = self.config.get_classrooms()
            wifi_config = {}
            
            if WIFI_CONFIG.exists():
                import json
                with open(WIFI_CONFIG) as f:
                    wifi_config = json.load(f)
            
            if request.method == 'POST':
                ssid = request.form.get('ssid', '').strip()
                password = request.form.get('password', '').strip()
                
                if ssid and password:
                    self.wifi_manager.save_credentials(ssid, password)
                    self.wifi_manager.connect(ssid, password)
                    status = self.wifi_manager.get_status()
            
            return render_template_string(
                self.base_html + self.wifi_html,
                status=status,
                networks=networks,
                saved_ssid=wifi_config.get('ssid', ''),
                saved_password=wifi_config.get('password', ''),
                offline_mode=self.config.get('offline_mode', True)
            )
        
        @self.app.route('/mode', methods=['POST'])
        def mode_settings():
            from flask import redirect, url_for
            offline_mode = 'offline_mode' in request.form
            self.config.set('offline_mode', offline_mode)
            return redirect(url_for('wifi_settings'))
        
        @self.app.route('/settings')
        def settings():
            from flask import render_template_string
            classrooms = self.config.get_classrooms()
            students = self.student_db.get_all_students()
            return render_template_string(
                self.base_html + self.settings_html,
                classrooms=classrooms,
                student_count=len(students),
                offline_mode=self.config.get('offline_mode', True)
            )
        
        @self.app.route('/classroom/add', methods=['POST'])
        def add_classroom():
            from flask import redirect, url_for, flash, request
            classroom = request.form.get('classroom', '').strip()
            if classroom:
                self.config.add_classroom(classroom, [])
                flash(f"Classroom {classroom} added!")
            return redirect(url_for('settings'))
        
        @self.app.route('/train', methods=['POST'])
        def train_model():
            from flask import redirect, url_for, flash
            students = self.student_db.get_all_students()
            if self.facial_rec.train_model([s['id'] for s in students]):
                flash("Model trained!")
            else:
                flash("Training failed!")
            return redirect(url_for('settings'))
        
        @self.app.route('/api/status')
        def api_status():
            from flask import jsonify
            return jsonify({
                'connected': self.wifi_manager.connected,
                'ssid': self.wifi_manager.current_ssid,
                'offline_mode': self.config.get('offline_mode', True),
                'student_count': len(self.student_db.get_all_students())
            })
    
    def run(self, host='0.0.0.0', port=5000):
        """Run the web server."""
        self.app.run(host=host, port=port, threaded=True)


# Main application
class StudentRecognitionApp:
    """Main application."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.wifi = WiFiManager()
        self.student_db = StudentDatabase()
        self.facial_rec = FacialRecognition()
        self.camera = CameraCapture()
        self._running = False
    
    def initialize(self):
        """Initialize components."""
        logger.info("Initializing Camp Tutor Student Management...")
        
        self.camera.initialize()
        
        if self.config.get('offline_mode', True):
            logger.info("Starting in OFFLINE mode")
        else:
            # Try connecting to WiFi if saved
            if self.wifi.has_saved_network():
                self.wifi.connect()
        
        # Initialize facial recognition
        self.facial_rec.initialize()
        
        logger.info("Camp Tutor initialized")
    
    def run(self):
        """Run the application."""
        self._running = True
        
        # Start web server
        server = WebServer(
            self.student_db,
            self.config,
            self.wifi,
            self.facial_rec
        )
        
        # Check if in focused/online mode
        if not self.config.get('offline_mode', True) and self.wifi.connected:
            logger.info("Running in FOCUSED ONLINE mode")
        
        # Run server
        server.run(port=self.config.get('server_port', 5000))
    
    def shutdown(self):
        """Clean shutdown."""
        self._running = False
        self.camera.close()
        logger.info("Camp Tutor shutdown")


def main():
    """Main entry point."""
    app = StudentRecognitionApp()
    app.initialize()
    
    try:
        app.run()
    except KeyboardInterrupt:
        pass
    finally:
        app.shutdown()


if __name__ == "__main__":
    main()