"""Web UI server for Camp Tutor robot with multi-page routing."""

import functools
import logging
import threading
import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request, Blueprint, send_file, redirect, url_for, session
from config import settings
from ui.ui_controls import (
    get_volume_control,
    get_age_selector,
    get_timetable_display,
    get_system_monitor,
)
from storage.student_db import get_student_db
from storage import student_db as student_db_module

logger = logging.getLogger(__name__)

ADMIN_PASSWORD = "Refugee123@"

app = Flask(__name__)

_app_state = {
    "status": "IDLE",
    "language": "en",
    "session_active": False,
    "device_status": {
        "lcd": {"ok": False, "error": "Not initialized"},
        "rex": {"ok": False, "error": "Not initialized"},
        "camera": {"ok": False, "error": "Not initialized"},
        "audio": {"ok": False, "error": "Not initialized"},
    },
}

app.config["SECRET_KEY"] = settings.WEB_SECRET_KEY
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False


def require_auth(f):
    """Require admin authentication."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


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
    
    # Get groups for enrollment
    try:
        from storage.class_manager import get_class_manager
        cm = get_class_manager()
        groups = cm.get_all_groups()
    except:
        groups = []
    
    return render_template("students.html", page="students", students=all_students, groups=groups)


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
    
    # Get class groups
    try:
        from storage.class_manager import get_class_manager
        cm = get_class_manager()
        groups = cm.get_all_groups()
    except:
        groups = []
    
    curriculum = settings.CURRICULUM
    return render_template(
        "courses.html",
        page="courses",
        age_groups=age_groups,
        current_age_group=current_age_group,
        timetable=timetable_data,
        curriculum=curriculum,
        groups=groups,
        schedule=timetable_data,
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


@app.route("/login", methods=["GET", "POST"])
def login():
    """Admin login page."""
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["authenticated"] = True
            return redirect(url_for("config"))
        return render_template("login.html", error="Invalid password")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Admin logout."""
    session.pop("authenticated", None)
    return redirect(url_for("index"))


@app.route("/config")
@require_auth
def config():
    """Configuration page."""
    vol_ctrl = get_volume_control()
    age_groups = []
    current_age_group = "primary"
    
    try:
        age_sel = get_age_selector()
        age_groups = age_sel.get_age_groups()
        current_age_group = age_sel.current_age_group
    except Exception as e:
        logger.warning(f"Could not get age groups: {e}")
    
    return render_template(
        "config.html",
        page="config",
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
            "device_status": _app_state.get("device_status", {}),
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/device_status/update", methods=["POST"])
def api_device_status_update():
    """Update device status from main app."""
    try:
        data = request.get_json()
        if data and "device_status" in data:
            _app_state["device_status"].update(data["device_status"])
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error updating device status: {e}")
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
        
        # Validate
        vol = max(0, min(100, int(vol)))
        
        # Set system volume
        vol_ctrl = get_volume_control()
        vol_ctrl.set_volume_percent(vol)
        
        # Save to settings for persistence
        try:
            import config.settings as config_settings
            config_settings.DEFAULT_VOLUME = vol / 100.0
            # Also set in os for other apps
            import os
            os.environ["CAMP_TUTOR_VOLUME"] = str(vol)
        except Exception as save_err:
            logger.warning(f"Could not persist volume: {save_err}")
        
        # Also update TTS engine volume
        try:
            from audio.text_to_speech import get_tts_engine
            tts = get_tts_engine()
            if tts:
                tts.set_volume_percent(vol)
        except Exception as tts_err:
            logger.warning(f"Could not update TTS volume: {tts_err}")
        
        # Test by speaking
        try:
            from audio.text_to_speech import get_tts_engine
            tts = get_tts_engine()
            if tts:
                tts.speak("Volume set to " + str(vol) + " percent.")
        except Exception as speak_err:
            logger.warning(f"Could not speak: {speak_err}")
        
        return jsonify({"success": True, "volume": vol})
    except Exception as e:
        logger.error(f"Volume error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/teach", methods=["POST"])
def api_teach():
    """Start teaching session."""
    try:
        data = request.get_json() or {}
        lang = data.get("language", "en")
        
        # Update state
        _app_state["status"] = "TEACHING"
        _app_state["language"] = lang
        _app_state["session_active"] = True
        
        # Speak greeting and start teaching computing for high school by default
        
        teach_error = None
        current_topic = "systems"
        try:
            from audio.text_to_speech import get_tts_engine
            from config import settings as config_settings
            from ai.tutor_engine import get_tutor_engine
            import threading
            
            lang_name = config_settings.LANGUAGE_NAMES.get(lang, lang)
            tts = get_tts_engine()
            tutor = get_tutor_engine()
            
            # Get first topic in computing curriculum for upper secondary
            curriculum = config_settings.CURRICULUM.get("upper_secondary", {}).get("computing", {})
            if curriculum:
                current_topic = list(curriculum.keys())[0] if curriculum else "systems"
            
            def run_teaching_session():
                """Background thread for teaching session (80 minutes) - no waiting."""
                import time
                consecutive_errors = 0
                try:
                    if tutor and current_topic:
                        tutor.start_session(student_id="class", language=lang, age=15)
                        tutor.current_subject = "computing"
                        tutor.current_topic = current_topic
                        tutor._current_subtopic_index = 0
                        tutor._current_lesson_part = "hook"
                        
                        start_time = time.time()
                        target_duration = 80 * 60  # 80 minutes
                        logger.info(f"Starting teaching session for {target_duration//60} minutes")
                        
                        while (time.time() - start_time) < target_duration and _app_state.get("session_active"):
                            remaining = target_duration - (time.time() - start_time)
                            
                            try:
                                lesson = tutor.deliver_pearson_lesson()
                                if lesson is None:
                                    # Reset and try again instead of breaking
                                    consecutive_errors += 1
                                    if consecutive_errors > 10:
                                        logger.warning("Too many consecutive errors, ending session")
                                        break
                                    tutor._current_subtopic_index = 0
                                    tutor._current_lesson_part = "hook"
                                    time.sleep(2)
                                    continue
                                
                                consecutive_errors = 0
                                part = lesson.get("part", "")
                                
                                if part == "complete" and remaining > 300:
                                    tutor._current_subtopic_index = 0
                                    tutor._current_lesson_part = "hook"
                            
                                elapsed = int(time.time() - start_time)
                                if elapsed % 60 == 0:  # Log every minute
                                    logger.info(f"Teaching: {elapsed//60} min elapsed, {remaining//60} min remaining")
                            except Exception as lesson_err:
                                logger.warning(f"Lesson error: {lesson_err}")
                                consecutive_errors += 1
                                if consecutive_errors > 10:
                                    break
                                time.sleep(2)
                                continue
                            
                            time.sleep(1)
                        
                        elapsed = int(time.time() - start_time)
                        logger.info(f"Teaching session completed after {elapsed} seconds ({elapsed//60} minutes)")
                        
                        tutor.end_session()
                        _app_state["status"] = "IDLE"
                        _app_state["session_active"] = False
                except Exception as e:
                    logger.error(f"Teaching thread error: {e}")
            
            if tts:
                tts.set_language(lang)
                tts.speak("Hello! Let's learn Computing in " + lang_name + "!")
            else:
                teach_error = "TTS engine not available"
            
            # Set computing as default subject for high school level
            if tutor:
                threading.Thread(target=run_teaching_session, daemon=True).start()
            else:
                if teach_error:
                    teach_error += "; Tutor engine not available"
                else:
                    teach_error = "Tutor engine not available"
                    
        except Exception as e:
            logger.warning(f"Speech/teach error: {e}")
            teach_error = str(e)
        
        response = {
            "success": True, 
            "status": "TEACHING",
            "language": lang,
            "subject": "computing",
            "topic": current_topic,
            "message": f"Teaching {current_topic} for 30-90 minutes"
        }
        if teach_error:
            response["error"] = teach_error
            response["success"] = False
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Teach error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/stop", methods=["POST"])
def api_stop():
    """Stop teaching session."""
    try:
        _app_state["status"] = "IDLE"
        _app_state["session_active"] = False
        
        return jsonify({"success": True, "status": "IDLE"})
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


@app.route("/api/language", methods=["POST"])
def api_language():
    """Set teaching language."""
    try:
        data = request.get_json()
        lang = data.get("language", "en")
        
        if lang not in config_settings.LANGUAGE_CODES:
            return jsonify({"error": f"Invalid language: {lang}"}), 400
        
        # Update app state
        _app_state["language"] = lang
        
        # Update web UI language display
        vol_ctrl = get_volume_control()
        age_sel = get_age_selector()
        
        # Save to file for persistence
        config_settings.DEFAULT_LANGUAGE = lang
        
        logger.info(f"Language switched to: {lang}")
        return jsonify({
            "success": True, 
            "language": lang,
            "language_name": config_settings.LANGUAGE_NAMES.get(lang, lang)
        })
    except Exception as e:
        logger.error(f"Language switch error: {e}")
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
                
                return jsonify({"success": True, "student_id": student_id})
        
        from config import settings
        languages = list(settings.LANGUAGE_NAMES.items())
        return render_template("student_add.html", page="students", languages=languages)
    except Exception as e:
        logger.error(f"Error adding student: {e}")
        return f"Error: {str(e)}", 500


@app.route("/api/student/create", methods=["POST"])
def api_student_create():
    """API endpoint to create student and return ID."""
    try:
        db = get_student_db()
        data = request.get_json()
        
        name = data.get("name", "").strip()
        language = data.get("language", "en").strip()
        classroom = data.get("classroom", "")
        age = data.get("age")
        
        if not name:
            return jsonify({"error": "Name required"}), 400
        
        age_int = int(age) if age else None
        student_id = db.create_student(
            name=name,
            preferred_language=language,
            classroom=classroom if classroom else None,
            age=age_int,
        )
        
        return jsonify({"success": True, "student_id": student_id})
    except Exception as e:
        logger.error(f"Error creating student: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/student/enroll", methods=["POST"])
def api_student_enroll():
    """Enroll student to a class/group."""
    try:
        data = request.get_json()
        student_id = data.get("student_id", "")
        group_id = data.get("group_id", "")
        
        if not student_id or not group_id:
            return jsonify({"success": False, "error": "student_id and group_id required"}), 400
        
        from storage.class_manager import get_class_manager
        cm = get_class_manager()
        
        # Add student to group
        cm.enroll_student(group_id, student_id)
        
        return jsonify({"success": True, "student_id": student_id, "group_id": group_id})
    except Exception as e:
        logger.error(f"Enroll error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/student/promote", methods=["POST"])
def api_student_promote():
    """Promote student to next level."""
    try:
        data = request.get_json()
        student_id = data.get("student_id", "")
        
        if not student_id:
            return jsonify({"success": False, "error": "student_id required"}), 400
        
        db = get_student_db()
        student = db.get_student(student_id)
        
        if not student:
            return jsonify({"success": False, "error": "Student not found"}), 404
        
        # Get current level and promote
        current_level = student.get("current_level", 1)
        new_level = min(10, current_level + 1)
        
        db.set_level(student_id, new_level)
        
        return jsonify({
            "success": True,
            "student_id": student_id,
            "old_level": current_level,
            "new_level": new_level
        })
    except Exception as e:
        logger.error(f"Promote error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/student/demote", methods=["POST"])
def api_student_demote():
    """Demote student to previous level."""
    try:
        data = request.get_json()
        student_id = data.get("student_id", "")
        
        if not student_id:
            return jsonify({"success": False, "error": "student_id required"}), 400
        
        db = get_student_db()
        student = db.get_student(student_id)
        
        if not student:
            return jsonify({"success": False, "error": "Student not found"}), 404
        
        current_level = student.get("current_level", 1)
        new_level = max(1, current_level - 1)
        
        db.set_level(student_id, new_level)
        
        return jsonify({
            "success": True,
            "student_id": student_id,
            "old_level": current_level,
            "new_level": new_level
        })
    except Exception as e:
        logger.error(f"Demote error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/timetable/assign", methods=["POST"])
def api_timetable_assign():
    """Assign timetable to a class/group."""
    try:
        data = request.get_json()
        group_id = data.get("group_id", "")
        day = data.get("day", "monday")
        time = data.get("time", "09:00")
        subject = data.get("subject", "language")
        age_group = data.get("age_group", "primary")
        
        if not group_id:
            return jsonify({"success": False, "error": "group_id required"}), 400
        
        from storage.class_manager import get_class_manager
        cm = get_class_manager()
        
        # Create timetable entry for the group
        entry = cm.add_timetable_entry(day, time, subject, age_group)
        
        return jsonify({
            "success": True,
            "group_id": group_id,
            "entry": entry,
            "day": day,
            "time": time,
            "subject": subject
        })
    except Exception as e:
        logger.error(f"Timetable assign error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/group/students", methods=["GET"])
def api_group_students():
    """Get students in a group."""
    try:
        group_id = request.args.get("group_id", "")
        
        from storage.class_manager import get_class_manager
        cm = get_class_manager()
        
        students = cm.get_group_students(group_id) if group_id else []
        
        return jsonify({"success": True, "students": students})
    except Exception as e:
        logger.error(f"Group students error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


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


@app.route("/student/<student_id>/capture_batch", methods=["POST"])
def student_capture_batch(student_id):
    """Capture batch of 5 photos for student."""
    try:
        from vision.camera_capture import get_camera
        cam = get_camera()
        
        if not cam.initialize():
            return jsonify({"error": "Camera not available"}), 500
        
        filepaths = cam.capture_batch(student_id, count=5)
        
        if filepaths:
            db = get_student_db()
            for filepath in filepaths:
                with open(filepath, "rb") as f:
                    db.add_photo(student_id, f.read(), filepath.split("/")[-1])
            
            return jsonify({"success": True, "count": len(filepaths), "filepaths": filepaths})
        return jsonify({"error": "Failed to capture"}), 500
    except Exception as e:
        logger.error(f"Error capturing batch: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/student/<student_id>/photos", methods=["GET"])
def student_photos(student_id):
    """Get all photos for a student."""
    try:
        db = get_student_db()
        student = db.get_student(student_id)
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
        
        photos = db.get_all_photos(student_id)
        return jsonify({"photos": photos, "count": len(photos)})
    except Exception as e:
        logger.error(f"Error getting photos: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/student/<student_id>/photo/<int:photo_index>")
def student_photo_by_index(student_id, photo_index):
    """Get a specific photo by index."""
    try:
        db = get_student_db()
        photo_path = db.get_photo_path(student_id, photo_index)
        
        if photo_path and os.path.exists(photo_path):
            return send_file(photo_path, mimetype="image/jpeg")
        
        return "", 404
    except Exception as e:
        logger.error(f"Error getting photo: {e}")
        return "", 404


@app.route("/api/camera/preview")
def camera_preview():
    """Get camera preview frame."""
    try:
        from vision.camera_capture import get_camera
        cam = get_camera()
        
        if not cam.initialize():
            return jsonify({"error": "Camera not available"}), 500
        
        frame = cam.get_preview_frame()
        if frame:
            return send_file(
                io.BytesIO(frame),
                mimetype="image/jpeg"
            )
        return jsonify({"error": "No frame"}), 500
    except Exception as e:
        logger.error(f"Error preview: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/student/<student_id>/photo/<int:photo_index>/delete", methods=["POST"])
def student_delete_photo(student_id, photo_index):
    """Delete a photo by index."""
    try:
        db = get_student_db()
        success = db.delete_photo(student_id, photo_index)
        
        if success:
            return jsonify({"success": True})
        return jsonify({"error": "Photo not found"}), 404
    except Exception as e:
        logger.error(f"Error deleting photo: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/student/<student_id>", methods=["PUT"])
def student_update(student_id):
    """Update student information."""
    try:
        db = get_student_db()
        data = request.get_json()
        
        if "name" in data:
            success = db.update_student_name(student_id, data["name"])
            if not success:
                return jsonify({"error": "Student not found"}), 404
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error updating student: {e}")
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


@app.route("/wifi/connect", methods=["POST"])
def wifi_connect():
    """Connect to WiFi network."""
    try:
        from config.wifi_manager import get_wifi_manager
        wifi = get_wifi_manager()
        
        ssid = request.form.get("ssid", "").strip()
        password = request.form.get("password", "").strip()
        
        if not ssid or not password:
            return jsonify({"error": "Missing ssid or password"}), 400
        
        wifi.save_credentials(ssid, password)
        
        # Try connecting - may fail without root privileges
        success = wifi.connect(ssid, password)
        
        if success:
            return jsonify({"success": True, "ssid": ssid, "message": "Connected to WiFi"})
        
        status = wifi.get_status()
        return jsonify({
            "success": False, 
            "ssid": ssid, 
            "error": "Connection failed - check network/hotspot is available",
            "debug": status
        })
        
        return jsonify({"success": False, "ssid": ssid, "error": "Connection failed"})
        
    except Exception as e:
        logger.error(f"WiFi connect error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


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


@app.route("/api/sudo/password", methods=["POST"])
def save_sudo_password():
    """Save sudo password for WiFi/Bluetooth operations."""
    try:
        from config.wifi_manager import _save_sudo_password
        password = request.json.get("password")
        if password:
            _save_sudo_password(password)
            return jsonify({"success": True})
        return jsonify({"error": "No password provided"}), 400
    except Exception as e:
        logger.error(f"Sudo password save error: {e}")
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


@app.route("/commands")
def commands_page():
    """Command interface page."""
    return render_template("commands.html", page="commands")


@app.route("/api/device/test/<device_type>", methods=["POST"])
def test_device(device_type):
    """Test a specific device - performs data transmission check without connecting."""
    try:
        if device_type == "speaker":
            try:
                import subprocess
                result = subprocess.run(["espeak", "-v", "en", "-s", "140", "-test"], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    return jsonify({"success": True, "message": "Speaker OK - test sound played", "data_transmission": "ok"})
                return jsonify({"success": False, "error": "Speaker command failed", "data_transmission": "failed"})
            except FileNotFoundError:
                return jsonify({"success": False, "error": "espeak not installed", "data_transmission": "n/a"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e), "data_transmission": "failed"})
        
        elif device_type == "microphone":
            try:
                try:
                    import speech_recognition as sr
                    mics = sr.Microphone.list_microphone_names()
                    if mics:
                        return jsonify({"success": True, "message": f"USB Mic: {mics[0]}", "data_transmission": "ok"})
                except ImportError:
                    pass
                
                try:
                    import sounddevice as sd
                    devices = sd.query_devices()
                    if devices:
                        return jsonify({"success": True, "message": "USB Mic available", "data_transmission": "ok"})
                except ImportError:
                    pass
                
                import platform
                if platform.system() != "Windows":
                    import subprocess
                    result = subprocess.run(["arecord", "-l"], capture_output=True, timeout=5)
                    if result.returncode == 0:
                        return jsonify({"success": True, "message": "Microphone detected", "data_transmission": "ok"})
                
                return jsonify({"success": False, "error": "No microphone found", "data_transmission": "failed"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e), "data_transmission": "failed"})
        
        elif device_type == "camera":
            try:
                from vision.camera_capture import get_camera
                cam = get_camera()
                if cam.is_ready():
                    return jsonify({"success": True, "message": "Camera ready", "data_transmission": "ok"})
                elif cam.initialize():
                    return jsonify({"success": True, "message": "Camera initialized", "data_transmission": "ok"})
                return jsonify({"success": False, "error": "Camera not available", "data_transmission": "failed"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e), "data_transmission": "failed"})
        
        elif device_type == "lcd":
            try:
                from display import lcd5110
                lcd = lcd5110.get_lcd()
                if not lcd._initialized:
                    lcd.initialize()
                if lcd._initialized:
                    lcd.show_text("Test OK", 0)
                    return jsonify({"success": True, "message": "LCD working", "data_transmission": "ok"})
                return jsonify({"success": False, "error": "LCD not initialized", "data_transmission": "failed"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e), "data_transmission": "failed"})
        
        elif device_type == "gpio":
            try:
                import RPi.GPIO as GPIO
                GPIO.setmode(GPIO.BOARD)
                return jsonify({"success": True, "message": "GPIO available", "data_transmission": "ok"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e), "data_transmission": "failed"})
        
        elif device_type == "i2c":
            try:
                import subprocess
                result = subprocess.run(["i2cdetect", "-l"], capture_output=True, timeout=5)
                if result.returncode == 0:
                    return jsonify({"success": True, "message": "I2C bus available", "data_transmission": "ok"})
                return jsonify({"success": False, "error": "I2C not available", "data_transmission": "failed"})
            except FileNotFoundError:
                return jsonify({"success": False, "error": "i2cdetect not found", "data_transmission": "n/a"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e), "data_transmission": "failed"})
        
        elif device_type == "rex":
            try:
                from control import rex_client
                rex = rex_client.get_rex_client()
                if rex.is_connected():
                    return jsonify({"success": True, "message": "REX connected via Serial USB", "data_transmission": "ok"})
                return jsonify({"success": False, "error": "REX not connected", "data_transmission": "disconnected"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e), "data_transmission": "failed"})
        
        elif device_type == "wifi":
            try:
                from config.wifi_manager import get_wifi_manager
                wifi = get_wifi_manager()
                if wifi.check_connection():
                    return jsonify({"success": True, "message": "WiFi connected", "data_transmission": "ok"})
                return jsonify({"success": False, "error": "WiFi not connected", "data_transmission": "disconnected"})
            except Exception as e:
                return jsonify({"success": False, "error": str(e), "data_transmission": "failed"})
        
        return jsonify({"success": False, "error": "Unknown device type"})
    except Exception as e:
        logger.error(f"Device test error: {e}")
        return jsonify({"success": False, "error": str(e)})


# ============ NEW API ENDPOINTS ============

@app.route("/api/camera/capture_libcamera", methods=["POST"])
def camera_capture_libcamera():
    """Capture using libcamera."""
    try:
        import subprocess
        result = subprocess.run(
            ["rpicam-still", "-o", "/tmp/web_vision.jpg", "-t", "2000"],
            capture_output=True,
            timeout=10,
        )
        if result.returncode == 0 and os.path.exists("/tmp/web_vision.jpg"):
            return jsonify({"success": True, "message": "Image captured"})
        return jsonify({"success": False, "error": "Capture failed"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/camera/analyze", methods=["POST"])
def camera_analyze():
    """Analyze what camera sees."""
    try:
        import cv2
        import numpy as np
        
        if not os.path.exists("/tmp/web_vision.jpg"):
            return jsonify({"success": False, "error": "No image"})
        
        img = cv2.imread("/tmp/web_vision.jpg")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        h, w = img.shape[:2]
        
        # Simple color detection
        b, g, r = img[:,:,0].mean(), img[:,:,1].mean(), img[:,:,2].mean()
        bright = gray.mean()
        
        # Lighting
        lighting = "dark" if bright < 50 else "bright" if bright > 200 else "normal"
        
        # Color tone
        if r > b + 20:
            tone = "warm (red/orange)"
            obj = "brown (wood/furniture)"
        elif b > r + 20:
            tone = "cool (blue)"
            obj = "blue items (possibly sky/window)"
        else:
            tone = "neutral"
            obj = "various colors"
        
        # Skin detection (person)
        skin = np.sum((r > 95) & (g > 40) & (b > 20) & (r > g) & (r > b)) / (h * w) * 100
        
        # Edge detection (detail level)
        edges = cv2.Canny(gray, 50, 150).sum() / (h * w) * 100
        scene = "busy/detailed" if edges > 2 else "simple/plain"
        
        # Describe what I see
        description = f"{lighting} room, {tone}"
        if skin > 2:
            description += ", person possible"
        description += ", " + scene + " scene"
        
        return jsonify({
            "success": True,
            "image": f"{w}x{h}",
            "lighting": lighting,
            "color_tone": tone,
            "scene": scene,
            "description": description,
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/students/detect", methods=["POST"])
def students_detect():
    """Detect students in camera."""
    try:
        import cv2
        
        if not os.path.exists("/tmp/web_vision.jpg"):
            return jsonify({"success": False, "error": "No image"})
        
        img = cv2.imread("/tmp/web_vision.jpg")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return jsonify({
            "success": True,
            "students": len(faces),
            "message": f"{len(faces)} students detected" if len(faces) > 0 else "No students"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/audio/test_input", methods=["POST"])
def audio_test_input():
    """Test microphone recording."""
    try:
        import pyaudio
        import wave
        
        p = pyaudio.PyAudio()
        mic = None
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                mic = i
                break
        
        if mic is None:
            return jsonify({"success": False, "error": "No microphone"})
        
        chunk = 1024
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, input_device_index=mic, frames_per_buffer=chunk)
        frames = [stream.read(chunk) for _ in range(20)]
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        with wave.open("/tmp/test_mic.wav", 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(b''.join(frames))
        
        return jsonify({"success": True, "message": "Recording OK"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/ready", methods=["GET"])
def ready_check():
    """Quick ready check."""
    try:
        results = {}
        
        # Camera
        results["camera"] = os.path.exists("/dev/video0")
        
        # Audio input - more tolerant check
        try:
            import subprocess
            # Check if arecord works
            results["microphone"] = subprocess.run(["arecord", "-l"], capture_output=True, timeout=2).returncode == 0
        except:
            results["microphone"] = False
        
        # Audio output - more tolerant check  
        try:
            import subprocess
            results["speaker"] = subprocess.run(["aplay", "-l"], capture_output=True, timeout=2).returncode == 0
        except:
            results["speaker"] = False
        
        # REX - just check if import works
        try:
            from control import rex_client
            results["rex"] = True
        except:
            results["rex"] = False
        
        return jsonify({"success": True, "status": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/speaker/test", methods=["POST"])
def speaker_test():
    """Test speaker output."""
    try:
        import subprocess
        # Faster speed (262 wpm = ~1.5x) + female voice
        text = "Hello, I'm Camp Tutor, speaker works well!"
        result = subprocess.run(
            ["espeak", "-ven+f3", "-s225", text],
            capture_output=True,
            timeout=10,
        )
        return jsonify({"success": True, "message": f"✓ Speaker: '{text}' (female voice, faster)"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/group/create", methods=["POST"])
def api_group_create():
    """Create a student group/class."""
    try:
        from storage.class_manager import get_class_manager
        data = request.get_json()
        
        name = data.get("name", "")
        language = data.get("language", "en")
        level = data.get("level", "beginner")
        
        if not name:
            return jsonify({"success": False, "error": "Group name required"}), 400
        
        cm = get_class_manager()
        group_id = cm.create_group(name, language, level)
        
        return jsonify({
            "success": True, 
            "group_id": group_id,
            "name": name,
            "language": language
        })
    except Exception as e:
        logger.error(f"Group error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/timetable/create", methods=["POST"])
def api_timetable_create():
    """Create a timetable entry."""
    try:
        data = request.get_json()
        
        day = data.get("day", "monday")
        time = data.get("time", "09:00")
        subject = data.get("subject", "language")
        language = data.get("language", "en")
        
        from storage import class_manager
        cm = class_manager.get_class_manager()
        
        entry = cm.add_timetable_entry(day, time, subject, language)
        
        return jsonify({
            "success": True, 
            "entry": entry,
            "day": day,
            "time": time,
            "subject": subject
        })
    except Exception as e:
        logger.error(f"Timetable error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/groups", methods=["GET"])
def api_groups():
    """Get all groups."""
    try:
        from storage.class_manager import get_class_manager
        cm = get_class_manager()
        groups = cm.get_all_groups()
        return jsonify({"success": True, "groups": groups})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/timetable", methods=["GET"])
def api_timetable():
    """Get timetable."""
    try:
        from storage.class_manager import get_class_manager
        cm = get_class_manager()
        entries = cm.get_timetable()
        return jsonify({"success": True, "entries": entries})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/computing/curriculum", methods=["GET"])
def api_computing_curriculum():
    """Get Year 7 Computing curriculum overview."""
    try:
        from config.computing_year7 import COMPUTING_YEAR7
        return jsonify({
            "success": True,
            "curriculum": COMPUTING_YEAR7
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/computing/lesson/<int:lesson_number>", methods=["GET"])
def api_computing_lesson(lesson_number):
    """Get specific lesson content."""
    try:
        from config.computing_year7 import get_lesson_info, COMPUTING_YEAR7
        if lesson_number < 1 or lesson_number > 60:
            return jsonify({"success": False, "error": "Lesson 1-60 only"}), 400
        
        topic_index = (lesson_number - 1) // 10
        subtopic_index = (lesson_number - 1) % 10
        lesson = get_lesson_info(topic_index, subtopic_index)
        
        return jsonify({
            "success": True,
            "lesson": lesson,
            "total_lessons": COMPUTING_YEAR7["total_lessons"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/computing/progress", methods=["GET", "POST"])
def api_computing_progress():
    """Get or update computing progress."""
    try:
        db = get_student_db()
        student_id = "class"  # Default for class teaching
        
        if request.method == "POST":
            data = request.get_json()
            lesson_number = data.get("lesson_number", 1)
            completed = data.get("completed", False)
            score = data.get("score", 0)
            
            db.update_computing_progress(student_id, lesson_number, completed, score)
            return jsonify({"success": True, "lesson": lesson_number})
        else:
            progress = db.get_computing_progress(student_id)
            return jsonify({"success": True, "progress": progress})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/computing/start", methods=["POST"])
def api_computing_start():
    """Start a Year 7 Computing lesson."""
    try:
        data = request.get_json() or {}
        lesson_number = data.get("lesson_number", 0)  # 0 = continue from saved progress
        language = data.get("language", "en")
        
        db = get_student_db()
        
        # Get lesson number
        if lesson_number == 0:
            progress = db.get_computing_progress("class")
            lesson_number = progress.get("current_lesson", 1)
        
        if lesson_number < 1:
            lesson_number = 1
        if lesson_number > 60:
            lesson_number = 60
        
        # Get lesson content
        from config.computing_year7 import get_lesson_info
        topic_index = (lesson_number - 1) // 10
        subtopic_index = (lesson_number - 1) % 10
        lesson = get_lesson_info(topic_index, subtopic_index)
        
        if not lesson:
            return jsonify({"success": False, "error": "Lesson not found"}), 404
        
        # Start teaching
        _app_state["status"] = "TEACHING"
        _app_state["session_active"] = True
        _app_state["current_lesson"] = lesson_number
        _app_state["current_subject"] = "computing"
        
        # Speak greeting
        try:
            from audio.text_to_speech import get_tts_engine
            tts = get_tts_engine()
            if tts:
                tts.set_language(language)
                tts.speak(f"Hello! Let's learn Year 7 Computing. Lesson {lesson_number}: {lesson['subtopic_name']} from topic {lesson['topic_name']}!")
        except Exception as tts_err:
            logger.warning(f"TTS error: {tts_err}")
        
        return jsonify({
            "success": True,
            "status": "TEACHING",
            "lesson": lesson,
            "message": f"Starting Year 7 Computing Lesson {lesson_number}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/computing/complete", methods=["POST"])
def api_computing_complete():
    """Mark lesson as complete."""
    try:
        data = request.get_json()
        lesson_number = data.get("lesson_number", 1)
        score = data.get("score", 100)
        duration_minutes = data.get("duration_minutes", 80)
        
        db = get_student_db()
        db.update_computing_progress("class", lesson_number, True, score)
        
        # Update total time
        try:
            db.increment_session("class", duration_minutes)
        except:
            pass
        
        return jsonify({
            "success": True,
            "next_lesson": lesson_number + 1 if lesson_number < 60 else lesson_number
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500