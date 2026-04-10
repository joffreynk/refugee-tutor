"""Configuration settings for Camp Tutor robot."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

HOSTNAME = "refugeetutor"
WEB_PORT = 5000
WEB_URL = f"http://{HOSTNAME}:{WEB_PORT}/"

I2C_SCL_PIN = 22
I2C_SDA_PIN = 21
I2C_ADDRESS = 0x42
I2C_SPEED_HZ = 100000

AUDIO_SAMPLE_RATE = 16000
AUDIO_CHUNK_SIZE = 1024
AUDIO_BUFFER_SIZE = 4096
AUDIO_MAX_DISTANCE = 500
AUDIO_NOISE_THRESHOLD = 0.02
AUDIO_NOISE_GATE_MS = 100
AUDIO_VOICE_ACTIVATION_THRESHOLD = 0.015
AUDIO_MIN_SNR_DB = 10
AUDIO_HIGH_PASS_FILTER_HZ = 80
AUDIO_LOW_PASS_FILTER_HZ = 8000
DEFAULT_VOLUME = 0.5
DEFAULT_SPEECH_RATE = 180

WAKE_WORD = "camp tutor"
WAKE_THRESHOLD = 0.5
INACTIVITY_TIMEOUT = 300

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FRAMERATE = 15

LCD_WIDTH = 84
LCD_HEIGHT = 48
LCD_CONTRAST = 0xBF
LCD_BIAS = 0x04

REX_LOOK_ANGLES = {
    "LEFT": (90, 45),
    "CENTER": (0, 30),
    "RIGHT": (-90, 45),
    "HOME": (0, 30),
}

REX_MOVE_DISTANCE = {
    "FWD": 30,
    "BACK": -30,
    "LEFT": 30,
    "RIGHT": -30,
}

REX_MIN_SAFE_DISTANCE = 20
REX_MAX_DISTANCE = 400
REX_MOVE_TIMEOUT = 5000
REX_COMM_TIMEOUT = 2000
DEFAULT_MOTOR_SPEED = 150

LANGUAGE_CODES = ["en", "zh", "hi", "ar", "fr", "bn", "pt", "ru", "id", "ur", "de", "ja", "pcm", "ar-eg", "mr", "vi", "te", "tr", "yue"]
LANGUAGE_NAMES = {
    "en": "English",
    "zh": "Mandarin Chinese",
    "hi": "Hindi",
    "ar": "Standard Arabic",
    "fr": "French",
    "bn": "Bengali",
    "pt": "Portuguese",
    "ru": "Russian",
    "id": "Indonesian",
    "ur": "Urdu",
    "de": "German",
    "ja": "Japanese",
    "pcm": "Nigerian Pidgin",
    "ar-eg": "Egyptian Arabic",
    "mr": "Marathi",
    "vi": "Vietnamese",
    "te": "Telugu",
    "tr": "Turkish",
    "yue": "Cantonese (Yue)",
}

AGE_GROUPS = {
    "early": {"min": 3, "max": 5, "name": "Early Years (3-5)"},
    "primary": {"min": 5, "max": 11, "name": "Primary (5-11)"},
    "lower_secondary": {"min": 11, "max": 14, "name": "Lower Secondary (11-14)"},
    "upper_secondary": {"min": 14, "max": 18, "name": "Upper Secondary (14-18)"},
}

CURRICULUM_SUBJECTS = [
    "mathematics",
    "science",
    "english",
    "global_citizenship",
    "computing",
    "programming",
]

TOPICS = CURRICULUM_SUBJECTS

DIFFICULTY_LEVELS = 10

CURRICULUM = {
    "early": {
        "mathematics": {
            "pre_number": {"intro": "Let's learn numbers!", "concepts": ["counting 1-10", "number recognition", "matching quantities", "more/less", "one more"]},
            "shapes": {"intro": "Let's explore shapes!", "concepts": ["basic 2D shapes", "sorting shapes", "patterns", "position", "symmetry"]},
            "measure": {"intro": "Let's measure!", "concepts": ["big/small", "long/short", "heavy/light", "capacity", "comparing"]},
        },
        "science": {
            "exploring": {"intro": "Let's discover!", "concepts": ["my body", "animals", "plants", "weather", "forces"]},
            "observations": {"intro": "What do you see?", "concepts": ["senses", "changes", "simple experiments", "materials"]},
        },
        "english": {
            "speaking": {"intro": "Let's talk!", "concepts": ["introductions", "describing", "questions", "listening"]},
            "listening": {"intro": "Listen carefully!", "concepts": ["instructions", "stories", "songs", "rhymes"]},
        },
        "global_citizenship": {
            "self": {"intro": "All about me!", "concepts": ["my family", "my school", "my community", "feelings"]},
            "environment": {"intro": "Our world!", "concepts": ["caring for nature", "helping others", "rules"]},
        },
        "computing": {
            "digital_literacy": {"intro": "Technology time!", "concepts": ["using tablets", "mouse skills", "coding basics"]},
        },
        "programming": {
            "unplugged": {"intro": "Let's code!", "concepts": ["directions", "sequences", "patterns", "loops"]},
        },
    },
    "primary": {
        "mathematics": {
            "number": {"intro": "Let's explore numbers!", "topics": ["place value", "addition", "subtraction", "multiplication", "division", "fractions", "decimals", "negative numbers"]},
            "geometry": {"intro": "Let's discover shapes!", "topics": ["2D shapes", "3D shapes", "angles", "symmetry", "coordinates", "transformations"]},
            "measure": {"intro": "Let's measure!", "topics": ["length", "mass", "time", "money", "perimeter", "area", "volume"]},
            "statistics": {"intro": "Let's organize data!", "topics": ["bar charts", "pictograms", "tables", "tally"]},
            "algebra": {"intro": "Patterns and rules!", "topics": ["sequences", "input/output", "simple expressions"]},
        },
        "science": {
            "biology": {"intro": "Living things!", "topics": ["living things", "habitats", "human body", "plants", "food chains", "ecosystems"]},
            "chemistry": {"intro": "Materials!", "topics": ["states of matter", "properties", "changing states", "rocks", "materials"]},
            "physics": {"intro": "How things work!", "topics": ["light", "sound", "forces", "electricity", "magnets", "energy"]},
        },
        "english": {
            "reading": {"intro": "Let's read!", "topics": ["comprehension", "vocabulary", "genres", "inference", "summarizing"]},
            "writing": {"intro": "Let's write!", "topics": ["narrative", "grammar", "spelling", "punctuation", "paragraphs"]},
            "speaking": {"intro": "Let's speak!", "topics": ["presentation", "discussion", "drama", "poetry"]},
        },
        "global_citizenship": {
            "world": {"intro": "Our world!", "topics": ["countries", "cultures", "traditions", "maps", "continents"]},
            "citizenship": {"intro": "Being a good citizen!", "topics": ["rights", "responsibilities", "environment", "community"]},
        },
        "computing": {
            "digital_systems": {"intro": "How computers work!", "topics": ["computer parts", "networks", "internet safety", "algorithms"]},
        },
        "programming": {
            "block_based": {"intro": "Let's code!", "topics": ["Scratch basics", "loops", "conditions", "events", "variables", "games"]},
        },
    },
    "lower_secondary": {
        "mathematics": {
            "number": {"intro": "Advanced numbers!", "topics": ["integers", "powers", "roots", "fractions", "percentages", "ratios", "standard form", "bounds"]},
            "algebra": {"intro": "Let's solve equations!", "topics": ["expressions", "equations", "graphs", "sequences", "inequalities", "formulae"]},
            "geometry": {"intro": "Geometry exploration!", "topics": ["angles", "polygons", "circles", "transformations", "congruence", "similarity", "Pythagoras"]},
            "statistics": {"intro": "Data analysis!", "topics": ["collection", "representation", " averages", "spread", "probability"]},
            "ratio": {"intro": "Proportions!", "topics": ["direct", "inverse", "scale drawings", "maps"]},
        },
        "science": {
            "biology": {"intro": "Biology fundamentals!", "topics": ["cells", "organisation", "infection", "bioenergetics", "homeostasis", "inheritance", "ecology"]},
            "chemistry": {"intro": "Chemistry basics!", "topics": ["particulate nature", "chemical reactions", "energy changes", "periodic table", "acids", "metals"]},
            "physics": {"intro": "Physics essentials!", "topics": ["forces", "waves", "electricity", "magnetism", "energy", "matter"]},
        },
        "english": {
            "literature": {"intro": "Explore literature!", "topics": ["fiction", "poetry", "drama", "analysis", "comparison", "context"]},
            "language": {"intro": "Language skills!", "topics": ["grammar", "writing styles", "presentation", "vocabulary", "spelling"]},
            "communication": {"intro": "Communication!", "topics": ["speaking", "listening", "group discussion", "presentation"]},
        },
        "global_citizenship": {
            "global_issues": {"intro": "World challenges!", "topics": ["climate change", "poverty", "migration", "inequality", "development"]},
            "sustainability": {"intro": "Our future!", "topics": ["environmental impact", "sustainable development", "resource management", "ecosystems"]},
            "politics": {"intro": "Understanding society!", "topics": ["democracy", "rights", "justice", "community"]},
        },
        "computing": {
            "systems": {"intro": "Computer systems!", "topics": ["hardware", "software", "networks", "cybersecurity", "data representation"]},
            "data": {"intro": "Data and algorithms!", "topics": ["binary", "databases", "computational thinking", "algorithms", "flowcharts"]},
        },
        "programming": {
            "python": {"intro": "Python programming!", "topics": ["syntax", "data types", "control flow", "functions", "files", "error handling"]},
            "web": {"intro": "Web development!", "topics": ["HTML", "CSS", "JavaScript basics", "web design", "accessibility"]},
        },
    },
    "upper_secondary": {
        "mathematics": {
            "pure": {"intro": "Pure mathematics!", "topics": ["algebra", "calculus", "trigonometry", "vectors", "sequences", "series", "complex numbers"]},
            "mechanics": {"intro": "Mechanics!", "topics": ["kinematics", "forces", "moments", "energy", "power", "momentum"]},
            "statistics": {"intro": "Statistics!", "topics": ["probability distributions", "hypothesis testing", "correlation", "regression", "normal distribution"]},
            "decision": {"intro": "Decision mathematics!", "topics": ["algorithms", "graph theory", "linear programming", "networks"]},
        },
        "science": {
            "physics": {"intro": "Advanced physics!", "topics": ["forces", "fields", "waves", "particles", "electricity", "materials", "nuclear"]},
            "chemistry": {"intro": "Advanced chemistry!", "topics": ["equilibria", "electrochemistry", "organic chemistry", "periodicity", "transition metals"]},
            "biology": {"intro": "Advanced biology!", "topics": ["genetics", "evolution", "ecosystems", "metabolism", "cell biology", "inheritance"]},
        },
        "english": {
            "literature": {"intro": "Literature analysis!", "topics": ["texts", "criticism", "comparison", "context", "theory", "drama"]},
            "language": {"intro": "Language analysis!", "topics": ["discourse", "representation", "sociolinguistics", "grammar", "orthography"]},
            "creative": {"intro": "Creative writing!", "topics": ["narrative", "poetry", "drama", "personal writing"]},
        },
        "global_citizenship": {
            "politics": {"intro": "Global politics!", "topics": ["governance", "human rights", "international relations", "terrorism", "conflict"]},
            "economics": {"intro": "Global economics!", "topics": ["development", "globalization", "trade", "markets", "finance"]},
            "environment": {"intro": "Environmental policy!", "topics": ["climate", "resources", "conservation", "sustainability"]},
        },
        "computing": {
            "theory": {"intro": "Computing theory!", "topics": ["computational complexity", "algorithms", "data structures", "computability", "formal languages"]},
            "systems": {"intro": "Systems architecture!", "topics": ["architecture", "networking", "operating systems", "databases", "security"]},
        },
        "programming": {
            "software": {"intro": "Software engineering!", "topics": ["OOP", "design patterns", "testing", "version control", "documentation"]},
            "advanced": {"intro": "Advanced programming!", "topics": ["algorithms", "databases", "APIs", "web services", "mobile"]},
        },
    },
}

STUDENT_DB_PATH = DATA_DIR / "students.db"
SESSION_LOG_PATH = DATA_DIR / "sessions"

DEFAULT_TTS_VOICE = {
    "en": "en-US",
    "zh": "zh-CN",
    "hi": "hi-IN",
    "ar": "ar-SA",
    "fr": "fr-FR",
    "bn": "bn-BD",
    "pt": "pt-BR",
    "ru": "ru-RU",
    "id": "id-ID",
    "ur": "ur-PK",
    "de": "de-DE",
    "ja": "ja-JP",
    "pcm": "en-NG",
    "ar-eg": "ar-EG",
    "mr": "mr-IN",
    "vi": "vi-VN",
    "te": "te-IN",
    "tr": "tr-TR",
    "yue": "yue-HK",
}

ROBOT_STATE = {
    "IDLE": "IDLE",
    "LISTENING": "LISTENING",
    "TEACHING": "TEACHING",
    "ENGAGED": "ENGAGED",
    "MOVING": "MOVING",
}

AGE_GROUP_KEYS = ["early", "primary", "lower_secondary", "upper_secondary"]
AGE_GROUP_DISPLAY = {
    "early": "Early Years (3-5)",
    "primary": "Primary (5-11)",
    "lower_secondary": "Lower Secondary (11-14)",
    "upper_secondary": "Upper Secondary (14-18)",
}

DEFAULT_LESSON_DURATION_MINUTES = 30
DEFAULT_TOPICS_PER_LESSON = 3

DAILY_SCHEDULE = {
    "early": {
        "start_time": "08:00",
        "end_time": "10:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "duration": 20},
            {"time": "08:25", "subject": "break", "duration": 5},
            {"time": "08:30", "subject": "english", "duration": 20},
            {"time": "08:55", "subject": "break", "duration": 10},
            {"time": "09:05", "subject": "science", "duration": 20},
        ],
    },
    "primary": {
        "start_time": "08:00",
        "end_time": "11:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "duration": 30},
            {"time": "08:35", "subject": "break", "duration": 5},
            {"time": "08:40", "subject": "english", "duration": 30},
            {"time": "09:15", "subject": "break", "duration": 10},
            {"time": "09:25", "subject": "science", "duration": 30},
        ],
    },
    "lower_secondary": {
        "start_time": "08:00",
        "end_time": "12:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "duration": 35},
            {"time": "08:40", "subject": "break", "duration": 5},
            {"time": "08:45", "subject": "english", "duration": 35},
            {"time": "09:25", "subject": "break", "duration": 10},
            {"time": "09:35", "subject": "science", "duration": 35},
        ],
    },
    "upper_secondary": {
        "start_time": "08:00",
        "end_time": "12:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "duration": 40},
            {"time": "08:45", "subject": "break", "duration": 5},
            {"time": "08:50", "subject": "english", "duration": 40},
            {"time": "09:35", "subject": "break", "duration": 10},
            {"time": "09:45", "subject": "science", "duration": 40},
        ],
    },
}

AI_MODE = "auto"

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")