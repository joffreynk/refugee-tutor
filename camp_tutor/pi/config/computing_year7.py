"""Year 7 Computing Curriculum - Pearson Edexcel Inspired.

6 Topics × 10 Subtopics = 60 Lessons
Each lesson: ~8 minutes for 80-minute interactive session
"""

COMPUTING_YEAR7 = {
    "grade": 7,
    "subject": "Computing",
    " syllabus": "Pearson Edexcel",
    "age_group": "lower_secondary",
    "total_lessons": 60,
    "lesson_duration_minutes": 8,
    "session_duration_minutes": 80,
    
    "topics": [
        {
            "id": "topic_1",
            "name": "Digital Literacy",
            "description": "Using computers safely and effectively",
            "subtopics": [
                {"id": "st_1_1", "name": "Getting Started with Computers", "keywords": ["computer", "hardware", "software", "mouse", "keyboard"]},
                {"id": "st_1_2", "name": "Operating Systems", "keywords": ["Windows", "Mac", "Linux", "interface"]},
                {"id": "st_1_3", "name": "File Management", "keywords": ["folder", "file", "save", "delete", "organise"]},
                {"id": "st_1_4", "name": "Typing Skills", "keywords": ["typing", "keyboard", "speed", "accuracy"]},
                {"id": "st_1_5", "name": "Online Safety", "keywords": ["password", "privacy", "safe", "internet"]},
                {"id": "st_1_6", "name": "Cyberbullying Awareness", "keywords": ["bullying", "online", "report", "support"]},
                {"id": "st_1_7", "name": "Reliable Information", "keywords": ["search", "reliable", "fake", "source"]},
                {"id": "st_1_8", "name": "Digital Footprint", "keywords": ["online", "footprint", "reputation", "social"]},
                {"id": "st_1_9", "name": "Health and Safety", "keywords": ["posture", "eye", "screen", "ergonomics"]},
                {"id": "st_1_10", "name": "Green Computing", "keywords": ["energy", "recycle", "environment", "sustainable"]}
            ]
        },
        {
            "id": "topic_2", 
            "name": "Algorithms & Logic",
            "description": "Introduction to programming thinking",
            "subtopics": [
                {"id": "st_2_1", "name": "What is an Algorithm?", "keywords": ["algorithm", "step", "instructions", "recipe"]},
                {"id": "st_2_2", "name": "Flowcharts", "keywords": ["flowchart", "diamond", "box", "decision"]},
                {"id": "st_2_3", "name": "Pseudocode", "keywords": ["pseudocode", "code", "writing"]},
                {"id": "st_2_4", "name": "Sequences", "keywords": ["sequence", "order", "step", "first"]},
                {"id": "st_2_5", "name": "Selection (If-Else)", "keywords": ["if", "else", "decision", "condition"]},
                {"id": "st_2_6", "name": "Iteration (Loops)", "keywords": ["loop", "repeat", "while", "for"]},
                {"id": "st_2_7", "name": "Debugging", "keywords": ["debug", "error", "fix", "problem"]},
                {"id": "st_2_8", "name": "Testing Algorithms", "keywords": ["test", "expected", "actual", "result"]},
                {"id": "st_2_9", "name": "Optimisation", "keywords": ["efficient", "faster", "better", "optimise"]},
                {"id": "st_2_10", "name": "Real-world Algorithms", "keywords": ["everyday", "life", "problem", "solve"]}
            ]
        },
        {
            "id": "topic_3",
            "name": "Data Representation",
            "description": "How computers store and process data",
            "subtopics": [
                {"id": "st_3_1", "name": "Binary Numbers", "keywords": ["binary", "0", "1", "bit", "digit"]},
                {"id": "st_3_2", "name": "Binary to Decimal", "keywords": ["convert", "decimal", "number", "base"]},
                {"id": "st_3_3", "name": "Hexadecimal", "keywords": ["hex", "16", "colour", "code"]},
                {"id": "st_3_4", "name": "Text Encoding (ASCII)", "keywords": ["ASCII", "character", "text", "letter"]},
                {"id": "st_3_5", "name": "Images (Pixels)", "keywords": ["pixel", "image", "resolution", "color"]},
                {"id": "st_3_6", "name": "Image Storage", "keywords": ["bitmap", "compress", "file", "size"]},
                {"id": "st_3_7", "name": "Sound Waves", "keywords": ["sound", "wave", "analog", "digital"]},
                {"id": "st_3_8", "name": "Digital Audio", "keywords": ["sample", "rate", "Hz", "quality"]},
                {"id": "st_3_9", "name": "Data Compression", "keywords": ["compress", "lossy", "lossless", "zip"]},
                {"id": "st_3_10", "name": "Units of Data", "keywords": ["byte", "KB", "MB", "GB", "TB"]}
            ]
        },
        {
            "id": "topic_4",
            "name": "Networks & Communication",
            "description": "How computers connect and share",
            "subtopics": [
                {"id": "st_4_1", "name": "What is a Network?", "keywords": ["network", "connect", "share", "devices"]},
                {"id": "st_4_2", "name": "LAN and WAN", "keywords": ["LAN", "WAN", "local", "wide"]},
                {"id": "st_4_3", "name": "Network Hardware", "keywords": ["router", "switch", "hub", "cable"]},
                {"id": "st_4_4", "name": "IP Addresses", "keywords": ["IP", "address", "number", "unique"]},
                {"id": "st_4_5", "name": "DNS", "keywords": ["DNS", "website", "name", "address"]},
                {"id": "st_4_6", "name": "The Internet", "keywords": ["internet", "web", "global", "world"]},
                {"id": "st_4_7", "name": "HTTP and HTTPS", "keywords": ["HTTP", "HTTPS", "secure", "web"]},
                {"id": "st_4_8", "name": "Email Protocols", "keywords": ["SMTP", "POP", "IMAP", "email"]},
                {"id": "st_4_9", "name": "WiFi Security", "keywords": ["WPA2", "password", "secure", "wifi"]},
                {"id": "st_4_10", "name": "Cloud Computing", "keywords": ["cloud", "storage", "online", "server"]}
            ]
        },
        {
            "id": "topic_5",
            "name": "Computer Systems",
            "description": "How computers work",
            "subtopics": [
                {"id": "st_5_1", "name": "Hardware Components", "keywords": ["CPU", "RAM", "hard", "drive"]},
                {"id": "st_5_2", "name": "The CPU", "keywords": ["processor", "CPU", "brain", "execute"]},
                {"id": "st_5_3", "name": "Memory (RAM)", "keywords": ["RAM", "memory", "temporary", "fast"]},
                {"id": "st_5_4", "name": "Storage Devices", "keywords": ["SSD", "HDD", "storage", "permanent"]},
                {"id": "st_5_5", "name": "Input Devices", "keywords": ["keyboard", "mouse", "input", "sensor"]},
                {"id": "st_5_6", "name": "Output Devices", "keywords": ["screen", "printer", "speaker", "output"]},
                {"id": "st_5_7", "name": "Operating Systems", "keywords": ["OS", "Windows", "system", "manage"]},
                {"id": "st_5_8", "name": "Application Software", "keywords": ["app", "software", "program", "application"]},
                {"id": "st_5_9", "name": "Boolean Logic", "keywords": ["AND", "OR", "NOT", "logic", "gate"]},
                {"id": "st_5_10", "name": "Performance", "keywords": ["speed", "cache", "boost", "performance"]}
            ]
        },
        {
            "id": "topic_6",
            "name": "Introduction to Python",
            "description": "Your first programming language",
            "subtopics": [
                {"id": "st_6_1", "name": "What is Programming?", "keywords": ["code", "program", "language", "Python"]},
                {"id": "st_6_2", "name": "Hello World", "keywords": ["print", "hello", "output", "string"]},
                {"id": "st_6_3", "name": "Variables", "keywords": ["variable", "store", "data", "name"]},
                {"id": "st_6_4", "name": "Data Types", "keywords": ["string", "integer", "float", "type"]},
                {"id": "st_6_5", "name": "User Input", "keywords": ["input", "ask", "user", "keyboard"]},
                {"id": "st_6_6", "name": "If Statements", "keywords": ["if", "else", "condition", "decision"]},
                {"id": "st_6_7", "name": "For Loops", "keywords": ["for", "loop", "range", "repeat"]},
                {"id": "st_6_8", "name": "While Loops", "keywords": ["while", "loop", "condition"]},
                {"id": "st_6_9", "name": "Lists", "keywords": ["list", "array", "store", "multiple"]},
                {"id": "st_6_10", "name": "Functions", "keywords": ["function", "def", "return", "reuse"]}
            ]
        }
    ]
}


def get_topic_by_id(topic_id: str) -> dict:
    """Get topic by ID."""
    for topic in COMPUTING_YEAR7["topics"]:
        if topic["id"] == topic_id:
            return topic
    return None


def get_subtopic(topic_id: str, subtopic_id: str) -> dict:
    """Get subtopic by ID."""
    topic = get_topic_by_id(topic_id)
    if topic:
        for st in topic["subtopics"]:
            if st["id"] == subtopic_id:
                return st
    return None


def get_lesson_info(topic_index: int, subtopic_index: int) -> dict:
    """Get lesson info for given indices."""
    if 0 <= topic_index < len(COMPUTING_YEAR7["topics"]):
        topic = COMPUTING_YEAR7["topics"][topic_index]
        if 0 <= subtopic_index < len(topic["subtopics"]):
            subtopic = topic["subtopics"][subtopic_index]
            lesson_num = topic_index * 10 + subtopic_index + 1
            return {
                "lesson_number": lesson_num,
                "topic_id": topic["id"],
                "topic_name": topic["name"],
                "subtopic_id": subtopic["id"],
                "subtopic_name": subtopic["name"],
                "keywords": subtopic["keywords"],
                "description": topic["description"],
                "duration_minutes": COMPUTING_YEAR7["lesson_duration_minutes"]
            }
    return None


def get_total_topics() -> int:
    return len(COMPUTING_YEAR7["topics"])


def get_total_subtopics() -> int:
    return len(COMPUTING_YEAR7["topics"]) * 10