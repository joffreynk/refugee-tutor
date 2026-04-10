"""Web UI server for Camp Tutor robot with multi-page routing."""

import logging
import threading
import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request, Blueprint, send_file, redirect, url_for
from ui.ui_controls import (
    get_volume_control,
    get_age_selector,
    get_timetable_display,
    get_system_monitor,
)
from bluetooth.bluetooth_manager import get_bluetooth_manager
from storage.student_db import get_student_db
from storage import student_db as student_db_module

logger = logging.getLogger(__name__)

app = Flask(__name__)

_app_state = {
    "status": "IDLE",
    "language": "en",
    "session_active": False,
}

app.config["SECRET_KEY"] = "camp-tutor-secret-key"


@app.route("/")
def index():
    """Dashboard - main overview."""
    devices = []
    status_ok = 0
    status_error = 0
    status_offline = 0
    
    try:
        sys_mon = get_system_monitor()
        dev_status = sys_mon.check_all_devices()
        for d in dev_status.values():
            devices.append({
                "name": d.name,
                "status": d.status,
                "details": d.details,
            })
            if d.status == "connected":
                status_ok += 1
            elif d.status == "error":
                status_error += 1
            else:
                status_offline += 1
    except Exception as e:
        logger.warning(f"Could not get device status: {e}")
    
    vol_ctrl = get_volume_control()
    age_sel = get_age_selector()
    
    return render_template(
        "dashboard.html", 
        page="dashboard",
        devices=devices,
        status_ok=status_ok,
        status_error=status_error,
        status_offline=status_offline,
        volume=vol_ctrl.volume_percent,
        muted=vol_ctrl.is_muted,
        age_group=age_sel.current_age_group_display,
    )


@app.route("/students")
def students():
    """List all students."""
    try:
        db = get_student_db()
        all_students = db.get_all_students()
    except:
        all_students = []
    return render_template("students.html", page="students", students=all_students)


@app.route("/courses")
def courses():
    """View and manage courses."""
    from config import settings
    try:
        age_sel = get_age_selector()
        timetable = get_timetable_display()
        age_groups = age_sel.get_age_groups()
        current_age_group = age_sel.current_age_group
        timetable_data = timetable.get_timetable()
    except:
        age_groups = []
        current_age_group = "primary"
        timetable_data = []
    
    curriculum = settings.CURRICULUM
    return render_template(
        "courses.html",
        page="courses",
        age_groups=age_groups,
        current_age_group=current_age_group,
        timetable=timetable_data,
        curriculum=curriculum,
    )


@app.route("/results")
def results():
    """View student results and assessments."""
    try:
        db = get_student_db()
        all_students = db.get_all_students()
        
        results_data = []
        for student in all_students:
            results_data.append({
                "student": student,
            })
    except:
        results_data = []
    
    return render_template("results.html", page="results", results=results_data)


@app.route("/progress")
def progress_view():
    """View overall progress and statistics."""
    try:
        age_sel = get_age_selector()
        timetable = get_timetable_display()
        
        summary = timetable.get_progress_summary()
        age_groups = age_sel.get_age_groups()
        current_age_group = age_sel.current_age_group
    except:
        summary = {}
        age_groups = []
        current_age_group = "primary"
    
    return render_template(
        "progress.html",
        page="progress",
        summary=summary,
        age_groups=age_groups,
        current_age_group=current_age_group,
    )


@app.route("/config")
def config():
    """Configuration page with Bluetooth settings."""
    bluetooth = {"state": "disconnected", "connected": None, "devices": []}
    vol_ctrl = get_volume_control()
    age_groups = []
    current_age_group = "primary"
    
    try:
        bt = get_bluetooth_manager()
        bluetooth = {
            "state": bt.state.value,
            "connected": bt.connected_device,
            "devices": [
                {"name": d.name, "address": d.address, "rssi": d.rssi, "connected": d.connected}
                for d in bt.discovered_devices
            ]
        }
    except Exception as e:
        logger.warning(f"Could not get bluetooth status: {e}")
    
    try:
        age_sel = get_age_selector()
        age_groups = age_sel.get_age_groups()
        current_age_group = age_sel.current_age_group
    except Exception as e:
        logger.warning(f"Could not get age groups: {e}")
    
    return render_template(
        "config.html",
        page="config",
        bluetooth=bluetooth,
        volume=vol_ctrl.volume_percent,
        muted=vol_ctrl.is_muted,
        age_groups=age_groups,
        current_age_group=current_age_group,
    )


@app.route("/api/status")
def api_status():
    """Get overall system status."""
    try:
        vol_ctrl = get_volume_control()
        age_sel = get_age_selector()
        
        return jsonify({
            "status": _app_state["status"],
            "age_group": age_sel.current_age_group_display,
            "volume": vol_ctrl.volume_percent,
            "language": _app_state["language"].upper(),
            "session_active": _app_state["session_active"],
            "muted": vol_ctrl.is_muted,
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/devices")
def api_devices():
    """Get device status of all connected devices."""
    try:
        sys_mon = get_system_monitor()
        devices = sys_mon.check_all_devices()
        
        device_list = []
        status_ok = 0
        status_error = 0
        status_offline = 0
        
        for d in devices.values():
            device_list.append({
                "name": d.name,
                "status": d.status,
                "details": d.details,
            })
            if d.status == "connected":
                status_ok += 1
            elif d.status == "error":
                status_error += 1
            else:
                status_offline += 1
        
        return jsonify({
            "devices": device_list,
            "summary": {
                "connected": status_ok,
                "error": status_error,
                "offline": status_offline,
                "total": len(device_list),
            }
        })
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return jsonify({"error": str(e), "devices": []}), 500


@app.route("/api/volume", methods=["POST"])
def api_volume():
    """Set volume."""
    try:
        data = request.get_json()
        vol = data.get("volume", 50)
        vol_ctrl = get_volume_control()
        vol_ctrl.set_volume_percent(vol)
        return jsonify({"success": True, "volume": vol})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/mute", methods=["POST"])
def api_mute():
    """Toggle mute."""
    try:
        vol_ctrl = get_volume_control()
        vol_ctrl.toggle_mute()
        return jsonify({"success": True, "muted": vol_ctrl.is_muted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/age_group", methods=["POST"])
def api_age_group():
    """Set age group."""
    try:
        data = request.get_json()
        key = data.get("age_group")
        age_sel = get_age_selector()
        age_sel.select_age_group_by_key(key)
        return jsonify({"success": True, "age_group": key})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/session", methods=["POST"])
def api_session():
    """Manage session."""
    try:
        data = request.get_json()
        action = data.get("action")
        
        if action == "start":
            _app_state["session_active"] = True
            _app_state["status"] = "ENGAGED"
        elif action == "end":
            _app_state["session_active"] = False
            _app_state["status"] = "IDLE"
        
        return jsonify({
            "success": True,
            "action": action,
            "session_active": _app_state["session_active"],
            "status": _app_state["status"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/state", methods=["POST"])
def api_state():
    """Set robot state."""
    try:
        data = request.get_json()
        state = data.get("state", "IDLE")
        _app_state["status"] = state
        return jsonify({"success": True, "status": state})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bluetooth/scan", methods=["POST"])
def api_bt_scan():
    """Scan for Bluetooth devices."""
    try:
        bt = get_bluetooth_manager()
        duration = request.json.get("duration", 10) if request.json else 10
        devices = bt.scan(duration)
        return jsonify({
            "success": True,
            "devices": [
                {"name": d.name, "address": d.address, "rssi": d.rssi, "connected": d.connected}
                for d in devices
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bluetooth/connect", methods=["POST"])
def api_bt_connect():
    """Connect to Bluetooth device."""
    try:
        data = request.get_json()
        address = data.get("address")
        bt = get_bluetooth_manager()
        success = bt.connect(address)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bluetooth/disconnect", methods=["POST"])
def api_bt_disconnect():
    """Disconnect from Bluetooth device."""
    try:
        bt = get_bluetooth_manager()
        success = bt.disconnect()
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bluetooth/status")
def api_bt_status():
    """Get Bluetooth status."""
    try:
        bt = get_bluetooth_manager()
        return jsonify({
            "state": bt.state.value,
            "connected": {
                "name": bt.connected_device.name,
                "address": bt.connected_device.address,
            } if bt.connected_device else None,
            "devices": [
                {"name": d.name, "address": d.address, "rssi": d.rssi, "connected": d.connected}
                for d in bt.discovered_devices
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/students")
def students_page():
    """Student management page."""
    try:
        db = get_student_db()
        all_students = db.get_all_students()
    except:
        all_students = []
    return render_template("students.html", page="students", students=all_students)


@app.route("/student/add", methods=["GET", "POST"])
def student_add():
    """Add new student."""
    try:
        db = get_student_db()
        
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            language = request.form.get("language", "en").strip()
            classroom = request.form.get("classroom", "").strip()
            age = request.form.get("age", "").strip()
            
            if name:
                age_int = int(age) if age else None
                student_id = db.create_student(
                    name=name,
                    preferred_language=language,
                    classroom=classroom if classroom else None,
                    age=age_int,
                )
                
                photo = request.files.get("photo")
                if photo and photo.filename:
                    db.add_photo(student_id, photo.read())
                
                return redirect(url_for("students_page"))
        
        from config import settings
        languages = list(settings.LANGUAGE_NAMES.items())
        return render_template("student_add.html", page="students", languages=languages)
    except Exception as e:
        logger.error(f"Error adding student: {e}")
        return f"Error: {str(e)}", 500


@app.route("/student/<student_id>")
def student_detail(student_id):
    """View student details."""
    try:
        db = get_student_db()
        student = db.get_student(student_id)
        
        if not student:
            return "Student not found", 404
        
        photo_path = db.get_photo_path(student_id)
        subjects_progress = db.get_all_subjects_progress(student_id)
        weak_topics = db.get_weak_topics(student_id)
        
        return render_template(
            "student_detail.html",
            page="students",
            student=student,
            photo_path=photo_path,
            subjects_progress=subjects_progress,
            weak_topics=weak_topics,
        )
    except Exception as e:
        logger.error(f"Error getting student: {e}")
        return f"Error: {str(e)}", 500


@app.route("/student/<student_id>/photo")
def student_photo(student_id):
    """Get student photo."""
    try:
        db = get_student_db()
        photo_path = db.get_photo_path(student_id)
        
        if photo_path and os.path.exists(photo_path):
            return send_file(photo_path, mimetype="image/jpeg")
        
        return "", 404
    except Exception as e:
        logger.error(f"Error getting photo: {e}")
        return "", 404


@app.route("/student/<student_id>/capture", methods=["POST"])
def student_capture_photo(student_id):
    """Capture photo for student using camera."""
    try:
        from vision.camera_capture import get_camera
        cam = get_camera()
        
        if not cam.initialize():
            return jsonify({"error": "Camera not available"}), 500
        
        filepath = cam.capture_for_student(student_id)
        
        if filepath:
            return jsonify({"success": True, "filepath": filepath})
        return jsonify({"error": "Failed to capture"}), 500
    except Exception as e:
        logger.error(f"Error capturing photo: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/student/<student_id>/delete", methods=["POST"])
def student_delete(student_id):
    """Delete a student."""
    try:
        db = get_student_db()
        success = db.delete_student(student_id)
        
        if success:
            return jsonify({"success": True})
        return jsonify({"error": "Student not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting student: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/wifi")
def wifi_page():
    """WiFi settings page."""
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        status = wifi.get_status()
        networks = wifi.scan_networks()
        
        return render_template(
            "wifi.html",
            page="wifi",
            status=status,
            networks=networks,
            saved_ssid=status.get("ssid", ""),
        )
    except Exception as e:
        logger.error(f"Error getting WiFi status: {e}")
        return render_template("wifi.html", page="wifi", status={}, networks=[], saved_ssid="")


@app.route("/bluetooth")
def bluetooth_page():
    """Bluetooth settings page."""
    return render_template("bluetooth.html", page="bluetooth")


@app.route("/wifi/connect", methods=["POST"])
def wifi_connect():
    """Connect to WiFi."""
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        
        ssid = request.form.get("ssid", "").strip()
        password = request.form.get("password", "").strip()
        
        if ssid and password:
            wifi.save_credentials(ssid, password)
            success = wifi.connect(ssid, password)
            
            return jsonify({"success": success, "ssid": ssid})
        
        return jsonify({"error": "Missing credentials"}), 400
    except Exception as e:
        logger.error(f"WiFi connect error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/wifi/disconnect", methods=["POST"])
def wifi_disconnect():
    """Disconnect from WiFi."""
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        wifi.disconnect()
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"WiFi disconnect error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/wifi/mode", methods=["POST"])
def wifi_mode():
    """Set offline/online mode."""
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        
        offline = request.json.get("offline", True)
        wifi.set_offline_mode(offline)
        
        return jsonify({"success": True, "offline_mode": offline})
    except Exception as e:
        logger.error(f"WiFi mode error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/wifi/scan")
def wifi_scan_api():
    """Scan for WiFi networks (API endpoint)."""
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        networks = wifi.scan_networks()
        return jsonify({"success": True, "networks": networks})
    except Exception as e:
        logger.error(f"WiFi scan error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/wifi/status")
def wifi_status_api():
    """Get WiFi status (API endpoint)."""
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        return jsonify({"success": True, "status": wifi.get_status()})
    except Exception as e:
        logger.error(f"WiFi status error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/camera/capture")
def camera_capture():
    """Capture camera frame for preview."""
    try:
        from vision.camera_capture import get_camera
        cam = get_camera()
        
        if not cam.initialize():
            return jsonify({"error": "Camera not available"}), 500
        
        frame = cam.get_preview_frame()
        
        if frame:
            return send_file(
                io.BytesIO(frame),
                mimetype="image/jpeg",
                as_attachment=False,
            )
        
        return jsonify({"error": "Failed to capture"}), 500
    except Exception as e:
        logger.error(f"Capture error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/camera/detect_faces")
def camera_detect_faces():
    """Detect faces in camera frame."""
    try:
        from vision.camera_capture import get_camera
        cam = get_camera()
        
        if not cam.initialize():
            return jsonify({"error": "Camera not available"}), 500
        
        faces = cam.detect_faces()
        
        return jsonify({"success": True, "faces": faces})
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/facial_recognition/train", methods=["POST"])
def facial_train():
    """Train facial recognition model."""
    try:
        from vision.facial_recognition import get_facial_recognition
        fr = get_facial_recognition()
        
        if not fr.initialize():
            return jsonify({"error": "Facial recognition not available"}), 500
        
        db = get_student_db()
        student_ids = [s["id"] for s in db.get_all_students()]
        
        success = fr.train_model(student_ids)
        
        return jsonify({"success": success})
    except Exception as e:
        logger.error(f"Training error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/facial_recognition/recognize")
def facial_recognize():
    """Recognize faces in uploaded image."""
    try:
        from vision.facial_recognition import get_facial_recognition
        fr = get_facial_recognition()
        
        if not fr.initialize():
            return jsonify({"error": "Facial recognition not available"}), 500
        
        if "image" not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        image_data = request.files["image"].read()
        results = fr.detect_and_recognize(image_data)
        
        return jsonify({"success": True, "results": results})
    except Exception as e:
        logger.error(f"Recognition error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/student/progress/<student_id>")
def student_progress_api(student_id):
    """Get student progress data."""
    try:
        db = get_student_db()
        student = db.get_student(student_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        subjects = db.get_all_subjects_progress(student_id)
        weak_topics = db.get_weak_topics(student_id)
        
        return jsonify({
            "student": student,
            "subjects": subjects,
            "weak_topics": weak_topics,
        })
    except Exception as e:
        logger.error(f"Error getting progress: {e}")
        return jsonify({"error": str(e)}), 500


import io


def run_server(host="0.0.0.0", port=500, debug=False):
    """Run the web server."""
    logger.info(f"Starting web server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


def start_server_thread(host="0.0.0.0", port=500):
    """Start web server in a separate thread."""
    server_thread = threading.Thread(
        target=run_server,
        kwargs={"host": host, "port": port, "debug": False},
        daemon=True,
    )
    server_thread.start()
    logger.info(f"Web server started on http://{host}:{port}")
    return server_thread


@app.route("/devices")
def devices_page():
    """Device status and testing page."""
    return render_template("devices.html", page="devices")


@app.route("/api/device/test/<device_type>", methods=["POST"])
def test_device(device_type):
    """Test a specific device."""
    try:
        if device_type == "speaker":
            try:
                import subprocess
                result = subprocess.run(["espeak", "-v", "en", "-s", "140", "-test"], 
                                      capture_output=True, timeout=5)
                return jsonify({"success": True, "message": "Speaker test sound played"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        elif device_type == "microphone":
            try:
                import subprocess
                result = subprocess.run(["arecord", "-l"], capture_output=True, timeout=5)
                if result.returncode == 0:
                    return jsonify({"success": True, "message": "Microphone detected"})
                return jsonify({"success": False, "error": "No microphone found"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        elif device_type == "camera":
            try:
                from vision.camera_capture import get_camera
                cam = get_camera()
                if cam.initialize():
                    return jsonify({"success": True, "message": "Camera initialized"})
                return jsonify({"success": False, "error": "Camera not available"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        elif device_type == "lcd":
            try:
                from display import lcd5110
                lcd = lcd5110.get_lcd()
                lcd.initialize()
                lcd.show_text("Test OK", 0)
                return jsonify({"success": True, "message": "LCD display working"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        elif device_type == "gpio":
            try:
                import RPi.GPIO as GPIO
                GPIO.setmode(GPIO.BOARD)
                return jsonify({"success": True, "message": "GPIO interface available"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        elif device_type == "i2c":
            try:
                import subprocess
                result = subprocess.run(["i2cdetect", "-l"], capture_output=True, timeout=5)
                return jsonify({"success": True, "message": "I2C bus available"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)})
        
        return jsonify({"success": False, "error": "Unknown device"})
    
    except Exception as e:
        logger.error(f"Device test error: {e}")
        return jsonify({"success": False, "error": str(e)})