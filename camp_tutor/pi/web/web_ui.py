"""Web UI server for Camp Tutor robot with multi-page routing."""

import logging
import threading
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request, Blueprint
from ui.ui_controls import (
    get_volume_control,
    get_age_selector,
    get_timetable_display,
    get_system_monitor,
)
from bluetooth.bluetooth_manager import get_bluetooth_manager
from storage.student_db import get_student_db

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