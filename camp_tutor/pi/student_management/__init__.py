"""Student Management package for Camp Tutor."""

from .student_recognition import (
    StudentDatabase,
    FacialRecognition,
    WiFiManager,
    ConfigManager,
    WebServer,
    StudentRecognitionApp,
)

__all__ = [
    "StudentDatabase",
    "FacialRecognition", 
    "WiFiManager",
    "ConfigManager",
    "WebServer",
    "StudentRecognitionApp",
]
