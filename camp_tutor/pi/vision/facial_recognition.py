"""Facial recognition module for student identification (offline)."""

import logging
import os
from pathlib import Path
from typing import Optional, Tuple

from config import settings

logger = logging.getLogger(__name__)

try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV not available - facial recognition disabled")


class FacialRecognition:
    """Facial recognition for student identification (works offline)."""

    def __init__(self):
        self._face_cascade = None
        self._recognizer = None
        self._model_path = settings.MODELS_DIR / "face_model.yml"
        self._initialized = False
        self._labels: dict = {}
        self._confidence_threshold = 0.6

    def initialize(self) -> bool:
        """Initialize facial recognition."""
        if self._initialized:
            return True

        if not HAS_CV2:
            logger.warning("OpenCV not available - facial recognition disabled")
            return False

        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            self._face_cascade = cv2.CascadeClassifier(cascade_path)

            if self._face_cascade.empty():
                logger.error("Failed to load face cascade")
                return False

            if self._model_path.exists():
                self._recognizer = cv2.face.LBPHFaceRecognizer_create()
                self._recognizer.read(str(self._model_path))
                self._load_labels()

            self._initialized = True
            logger.info("Facial recognition initialized")
            return True

        except Exception as e:
            logger.error(f"Facial recognition init error: {e}")
            return False

    def _load_labels(self) -> None:
        """Load label mapping from file."""
        labels_path = settings.MODELS_DIR / "face_labels.json"
        if labels_path.exists():
            try:
                import json
                with open(labels_path) as f:
                    self._labels = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load labels: {e}")

    def _save_labels(self) -> None:
        """Save label mapping to file."""
        try:
            settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
            import json
            with open(settings.MODELS_DIR / "face_labels.json", "w") as f:
                json.dump(self._labels, f)
        except Exception as e:
            logger.error(f"Failed to save labels: {e}")

    def detect_faces(self, image: bytes) -> list:
        """Detect faces in image."""
        if not self._initialized or not self._face_cascade:
            return []

        try:
            nparr = np.frombuffer(image, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return []

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
            )

            return faces.tolist() if len(faces) > 0 else []

        except Exception as e:
            logger.error(f"Face detection error: {e}")
            return []

    def recognize_face(self, face_image: bytes) -> Tuple[Optional[str], float]:
        """Recognize a face and return student ID and confidence."""
        if not self._initialized or self._recognizer is None:
            return None, 0.0

        try:
            nparr = np.frombuffer(face_image, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
            if img is None:
                return None, 0.0

            img = cv2.resize(img, (100, 100))
            label, confidence = self._recognizer.predict(img)

            if confidence < self._confidence_threshold * 100:
                student_id = self._labels.get(str(label), f"student_{label}")
                return student_id, 1.0 - (confidence / 100.0)

            return None, 0.0

        except Exception as e:
            logger.error(f"Face recognition error: {e}")
            return None, 0.0

    def detect_and_recognize(self, image: bytes) -> list:
        """Detect and recognize all faces in an image."""
        if not self._initialized:
            return []

        results = []
        faces = self.detect_faces(image)

        if not faces:
            return []

        try:
            nparr = np.frombuffer(image, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return []

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            for x, y, w, h in faces:
                face_roi = gray[y : y + h, x : x + w]
                face_roi_resized = cv2.resize(face_roi, (100, 100))

                if self._recognizer:
                    label, confidence = self._recognizer.predict(face_roi_resized)
                    if confidence < self._confidence_threshold * 100:
                        student_id = self._labels.get(str(label), f"student_{label}")
                        results.append({
                            "student_id": student_id,
                            "confidence": 1.0 - (confidence / 100.0),
                            "bbox": [x, y, w, h],
                        })
                    else:
                        results.append({
                            "student_id": None,
                            "confidence": 0.0,
                            "bbox": [x, y, w, h],
                        })
                else:
                    results.append({
                        "student_id": None,
                        "confidence": 0.0,
                        "bbox": [x, y, w, h],
                    })

        except Exception as e:
            logger.error(f"Detect and recognize error: {e}")

        return results

    def train_model(self, student_ids: list) -> bool:
        """Train face recognition model with student photos."""
        if not HAS_CV2:
            logger.warning("Cannot train - OpenCV not available")
            return False

        try:
            from PIL import Image

            images = []
            labels = []
            label_map = {}
            next_label = 0

            for idx, student_id in enumerate(student_ids):
                student_photos_dir = settings.DATA_DIR / "student_photos" / student_id
                if not student_photos_dir.exists():
                    continue

                label_map[student_id] = next_label

                for photo_file in sorted(student_photos_dir.glob("*.jpg")):
                    try:
                        img = Image.open(photo_file).convert("L")
                        img = img.resize((100, 100))
                        images.append(np.array(img))
                        labels.append(next_label)
                    except Exception:
                        continue

                next_label += 1

            if len(images) < 2:
                logger.warning("Not enough images to train model")
                return False

            self._recognizer = cv2.face.LBPHFaceRecognizer_create()
            self._recognizer.train(images, np.array(labels))

            settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
            self._recognizer.save(str(self._model_path))
            self._labels = {str(v): k for k, v in label_map.items()}
            self._save_labels()

            logger.info(f"Face model trained with {len(images)} images")
            return True

        except Exception as e:
            logger.error(f"Model training error: {e}")
            return False

    def add_student_face(self, student_id: str, photo_data: bytes) -> bool:
        """Add a student's face photo for future recognition."""
        try:
            student_photos_dir = settings.DATA_DIR / "student_photos" / student_id
            student_photos_dir.mkdir(parents=True, exist_ok=True)

            nparr = np.frombuffer(photo_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return False

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
            )

            if len(faces) == 0:
                logger.warning("No face detected in photo")
                return False

            x, y, w, h = faces[0]
            face_roi = gray[y : y + h, x : x + w]
            face_resized = cv2.resize(face_roi, (100, 100))

            import uuid
            filename = f"face_{uuid.uuid4().hex[:8]}.jpg"
            filepath = student_photos_dir / filename

            cv2.imwrite(str(filepath), face_resized)
            logger.info(f"Added face photo for student {student_id}")
            return True

        except Exception as e:
            logger.error(f"Add student face error: {e}")
            return False


_facial_recognition_instance: Optional[FacialRecognition] = None


def get_facial_recognition() -> FacialRecognition:
    """Get global facial recognition instance."""
    global _facial_recognition_instance
    if _facial_recognition_instance is None:
        _facial_recognition_instance = FacialRecognition()
    return _facial_recognition_instance