"""Configuration settings for Camp Tutor robot."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

HOSTNAME = "refugeetutor"
WEB_PORT = 5000
WEB_URL = f"http://{HOSTNAME}:{WEB_PORT}/"
WEB_SECRET_KEY = os.environ.get("WEB_SECRET_KEY", "camp-tutor-secret-key-change-in-production")

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
DEFAULT_SPEECH_RATE = 130
DEFAULT_LANGUAGE = "en"

WAKE_WORD = "hello tutor robot"
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

# REX Serial USB Connection
# REX ESP32 connects via USB Serial to Raspberry Pi
# Connect Pi USB port to REX USB/Serial header
REX_SERIAL_PORT = "/dev/ttyUSB0"
REX_SERIAL_BAUDRATE = 9600

# ILI9341 LCD Connection (SPI 8-pin to Raspberry Pi)
# Pin 1 VCC   → Pin 1  (3.3V)
# Pin 2 GND   → Pin 6  (GND)
# Pin 3 SCE   → Pin 24 (GPIO 8 / CE0) - Chip Select
# Pin 4 RST   → Pin 22 (GPIO 25)      - Reset
# Pin 5 D/C   → Pin 18 (GPIO 24)      - Data/Command
# Pin 6 MOSI  → Pin 19 (GPIO 10)      - SPI MOSI
# Pin 7 SCLK  → Pin 23 (GPIO 11)      - SPI Clock
# Pin 8 LED   → Pin 12 (GPIO 18)      - Backlight

LANGUAGE_CODES = ["en", "zh", "hi", "ar", "fr", "bn", "pt", "ru", "id", "ur", "de", "ja", "pcm", "ar-eg", "mr", "vi", "te", "tr", "yue", "es", "it"]
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
    "es": "Spanish",
    "it": "Italian",
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

COMPREHENSIVE_CURRICULUM = {
    "early": {
        "mathematics": {
            "topics": [
                {"name": "Numbers", "subtopics": ["counting_1_10"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Speaking", "subtopics": ["basic_sounds"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Our Bodies", "subtopics": ["body_parts"]},
            ]
        }
    },
    "primary": {
        "mathematics": {
            "topics": [
                {"name": "Number", "subtopics": ["place_value"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Reading", "subtopics": ["comprehension"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Biology", "subtopics": ["cells"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Digital Literacy", "subtopics": ["devices"]},
            ]
        }
    },
    "lower_secondary": {
        "mathematics": {
            "topics": [
                {"name": "Number", "subtopics": ["integers"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Literature", "subtopics": ["novels"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Biology", "subtopics": ["cells"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Computer Systems", "subtopics": ["hardware"]},
            ]
        }
    },
    "upper_secondary": {
        "mathematics": {
            "topics": [
                {"name": "Pure Math", "subtopics": ["algebra"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Literature", "subtopics": ["Shakespeare"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Physics", "subtopics": ["mechanics"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Systems", "subtopics": ["architecture"]},
            ]
        }
    }
}

CURRICULUM = COMPREHENSIVE_CURRICULUM

DIFFICULTY_LEVELS = 10

PEARSON_CURRICULUM = {
    "upper_secondary": {
        "computing": {
            "systems": {
                "duration_minutes": 90,
                "subtopics": [
                    {
                        "name": "Computer Systems Architecture",
                        "duration": 90,
                        "hook": "Did you know your smartphone has more computing power than the computers that took astronauts to the Moon? Today, we're going on an incredible journey inside computers to understand how they think, process information, and power the digital world around us. This is computer systems architecture!",
                        "sections": [
                            {
                                "title": "Introduction to Computer Architecture",
                                "duration": 5,
                                "content": """Welcome to your journey into Computer Systems Architecture! I'm your Pearson Edexcel certified master teacher, and I'm excited to guide you through this fundamental topic in computing.

Computer architecture is the blueprint of how computers work internally. It's the design that allows your phone, laptop, and every digital device to perform amazing tasks. Understanding architecture helps you become a better programmer and system designer.

Every computer, from a simple calculator to a supercomputer, follows architectural principles. These principles have evolved over decades but remain rooted in fundamental concepts we'll explore together.

By the end of this lesson, you'll understand how computers process instructions, how they store and retrieve data, and how different components work together. You'll see why your computer can execute billions of operations per second and how engineers design systems for speed and efficiency."""
                            },
                            {
                                "title": "The Heart of the Computer: CPU Architecture",
                                "duration": 20,
                                "content": """Now let's explore the Central Processing Unit, the brain of your computer. The CPU is where all the magic happens - it's the component that executes instructions and processes data.

The CPU has three main parts working together. First, the Control Unit fetches instructions from memory. It acts like a traffic controller, directing data to where it needs to go. Second, the Arithmetic Logic Unit, called the ALU, performs all mathematical calculations and logical operations. Third, registers are tiny storage locations inside the CPU that hold data being processed.

The fetch-decode-execute cycle is the heartbeat of every computer. It repeats billions of times per second! In the fetch step, the CPU retrieves an instruction from memory. The instruction is a binary number - just zeros and ones - that represents a specific command.

In the decode step, the control unit interprets the instruction. It determines what operation needs to happen - should the CPU add numbers, compare values, or move data? Different binary patterns mean different instructions.

In the execute step, the ALU performs the actual operation. If it's an addition, the ALU adds the numbers. If it's a comparison, the ALU determines if one value is greater, equal, or less than another.

Modern CPUs are incredibly fast. They can execute billions of these cycles per second! A processor rated at 3 gigahertz performs three billion cycles per second.

But speed isn't everything. CPU designers also focus on efficiency. They use techniques like pipelining, where multiple instructions are processed simultaneously at different stages. It's like an assembly line in a factory - while one instruction is being executed, the next is being decoded, and another is being fetched.

Cache memory makes CPUs even faster. Cache is a small amount of very fast memory located directly on the CPU chip. It stores frequently used data and instructions, reducing the time needed to access main memory.

CPUs have multiple levels of cache - L1, L2, and sometimes L3. L1 is the fastest and smallest. L2 is larger but slightly slower. This hierarchy balances speed and capacity."""
                            },
                            {
                                "title": "Memory Hierarchy and Storage",
                                "duration": 15,
                                "content": """Let's explore memory - how computers store and retrieve information. Understanding memory hierarchy is crucial for writing efficient programs.

RAM, or Random Access Memory, is your computer's working memory. When you open a program, it loads into RAM so the CPU can access it quickly. RAM is fast but temporary - when you turn off your computer, everything in RAM disappears.

RAM is organized in rows and columns. Each location has an address, and any location can be accessed equally quickly. This is different from storage media like hard drives where accessing different locations takes different amounts of time.

The speed gap between RAM and storage is enormous. RAM can transfer data at billions of bytes per second, while storage is much slower. This is why having enough RAM is crucial for computer performance.

When RAM is full, your computer uses part of the hard drive as virtual memory. This is much slower, which is why your computer slows down when you have too many programs open.

Read-Only Memory, or ROM, stores permanently saved data. It contains instructions that run when you first turn on your computer - this is called the bootstrap process. Unlike RAM, ROM keeps its contents even when the computer is off.

Solid-state drives, or SSDs, are modern storage using flash memory. They're much faster than traditional hard drives because they have no moving parts. Accessing data on an SSD is nearly as fast as accessing data in RAM for many operations.

Understanding memory helps you make smart programming decisions. Reading from cache is much faster than reading from RAM, which is much faster than reading from storage. Good programmers organize data to take advantage of this hierarchy."""
                            },
                            {
                                "title": "Data Representation and Binary Systems",
                                "duration": 15,
                                "content": """Everything in a computer - every photo, every song, every program - is stored as numbers! Let's understand how computers represent data.

Computers use binary, which means just two digits: 0 and 1. This is because computers work with electricity, and electricity is either on or off. On represents 1, off represents 0.

A single binary digit is called a bit. Eight bits make a byte. With just 8 bits, we can represent 256 different values (2 to the power of 8). That's enough for all uppercase and lowercase letters, numbers, and common symbols!

Integers work simply in binary. The number 5 is 00000101 in binary. Each position represents a power of 2: 1, 2, 4, 8, 16, and so on. So 5 = 4 + 1, which is 00000101.

Negative numbers use two's complement. This clever system lets computers use the same circuits for addition and subtraction. To find the negative of a number, invert all bits and add 1.

Text uses character encoding. ASCII assigns each character a number. 'A' is 65, 'a' is 97, '0' is 48. Unicode extends this to include characters from all world languages and symbols.

Images are grids of pixels. Each pixel has color values. With 8 bits each for red, green, and blue, we get over 16 million possible colors. Your phone's camera likely captures millions of pixels!

Sound is stored as samples. The computer measures the sound wave thousands of times per second and stores each measurement. CD quality uses 44,100 samples per second, with 16 bits per sample.

Understanding data representation helps you choose appropriate data types, understand why some calculations produce unexpected results, and work with different file formats."""
                            },
                            {
                                "title": "Input/Output and Peripheral Systems",
                                "duration": 10,
                                "content": """Computers need to communicate with the outside world through Input and Output, called I/O. Let's explore how computers interact with users and other devices.

Input devices send data to the CPU. Keyboards, mice, touchscreens, microphones, and cameras are all input devices. Each converts physical input - your key press, your voice, light - into binary data the computer can process.

Output devices present data to users or other systems. Monitors, speakers, and printers are output devices. They convert binary data into human-perceivable forms - images, sound, or physical documents.

The Operating System manages I/O devices through drivers. These are specialized programs that translate general commands into device-specific instructions.

Universal Serial Bus, or USB, is the most common connection type. USB supports many device types through a single connection. USB-C is the latest version, offering faster speeds and reversible connectors.

Display systems have evolved dramatically. Early computers showed green text on black screens. Modern displays show millions of colors at high resolutions. Your phone likely has a display with over a million pixels!

Graphics Processing Units, or GPUs, are specialized processors for images and video. They can process thousands of pixels simultaneously, making them essential for gaming and graphics-intensive applications.

Bluetooth enables wireless connections to peripherals. You can connect headphones, keyboards, and mice without cables. This uses short-range radio waves to communicate.""",
                                "quiz": []
                            },
                            {
                                "title": "The Complete System: How Everything Works Together",
                                "duration": 20,
                                "content": """Let's see how all the components work together as one unified system. This is where computer architecture becomes truly fascinating!

When you turn on your computer, the CPU executes instructions from ROM. These instructions initialize hardware components and load the operating system from storage into RAM. This is called booting.

Once the operating system is loaded, it manages resources and provides services to programs. When you click an icon, the operating system tells the CPU to run that program, which loads into RAM.

Programs interact with hardware through the operating system. They don't need to know the details of how your specific printer works - the operating system handles that through drivers.

Processes are running programs. The operating system rapidly switches between processes, giving the illusion that many programs run simultaneously. This is called time-sharing.

Each process has its own memory space. This isolation prevents one program from interfering with another. If one program crashes, others keep running.

The file system organizes data on storage. Files are organized in folders (directories), which can contain other folders. This creates a hierarchical structure like an upside-down tree.

Networks connect computers together. Your home router connects to your Internet Service Provider, which connects to other networks. When you visit a website, data travels through multiple networks to reach you.

Protocols are rules for network communication. TCP/IP is the fundamental protocol. HTTP sends web pages, HTTPS adds security, and email protocols handle messages.

Security is essential in modern systems. Firewalls block unauthorized access. Encryption protects data as it travels. Authentication verifies user identity before granting access.

Understanding the complete system helps you troubleshoot problems, optimize performance, and design better software. Every concept we've explored connects to create the powerful machines we use every day.""",
                                "quiz": [
                                    "What is the fetch-decode-execute cycle and why is it important?",
                                    "Explain the difference between RAM and storage. Why does this matter for performance?",
                                    "How does binary representation allow computers to store all types of data?",
                                    "What role does the operating system play in connecting programs to hardware?",
                                    "Why is cache memory important for CPU performance?"
                                ]
                            }
                        ]
                    }
                ]
            }
        }
    }
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

DEFAULT_LESSON_DURATION_MINUTES = 80
DEFAULT_TOPICS_PER_LESSON = 5
SUBTOPICS_PER_TOPIC = 1

# Comprehensive Curriculum: 5 Topics × 1 Subtopic per Level
COMPREHENSIVE_CURRICULUM = {
    "early": {
        "mathematics": {
            "topics": [
                {"name": "Numbers", "subtopics": ["counting_1_10"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Speaking", "subtopics": ["basic_sounds"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Our Bodies", "subtopics": ["body_parts"]},
            ]
        }
    },
    "primary": {
        "mathematics": {
            "topics": [
                {"name": "Number", "subtopics": ["place_value"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Reading", "subtopics": ["comprehension"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Biology", "subtopics": ["cells"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Digital Literacy", "subtopics": ["devices"]},
            ]
        }
    },
    "lower_secondary": {
        "mathematics": {
            "topics": [
                {"name": "Number", "subtopics": ["integers"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Literature", "subtopics": ["novels"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Biology", "subtopics": ["cells"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Computer Systems", "subtopics": ["hardware"]},
            ]
        }
    },
    "upper_secondary": {
        "mathematics": {
            "topics": [
                {"name": "Pure Math", "subtopics": ["algebra"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Literature", "subtopics": ["Shakespeare"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Physics", "subtopics": ["mechanics"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Systems", "subtopics": ["architecture"]},
            ]
        }
    }
}

COMPREHENSIVE_CURRICULUM = {
    "early": {
        "mathematics": {
            "topics": [
                {"name": "Numbers", "subtopics": ["counting", "ordering", "more_less", "adding", "subtracting", "sharing"]},
                {"name": "Shapes", "subtopics": ["circles", "squares", "triangles", "patterns", "position", "symmetry"]},
                {"name": "Measurement", "subtopics": ["length", "weight", "time", "money", "capacity", "temperature"]},
                {"name": "Patterns", "subtopics": ["colour_patterns", "shape_patterns", "number_patterns", "growing", "sharing", "creating"]},
                {"name": "Problem Solving", "subtopics": ["counting", "sharing", "making", "real_life", "games", "puzzles"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Speaking", "subtopics": ["sounds", "words", "sentences", "stories", "rhymes", "songs"]},
                {"name": "Listening", "subtopics": ["sounds", "stories", "instructions", "questions", " conversations", "rhymes"]},
                {"name": "Reading", "subtopics": ["letters", "words", "books", "pictures", "stories", "signs"]},
                {"name": "Writing", "subtopics": ["marks", "letters", "words", "drawing", "stories", "labels"]},
                {"name": "Phonics", "subtopics": ["sounds", "blending", "segmenting", "reading", "writing", "games"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Our Bodies", "subtopics": ["parts", "senses", "healthy", "exercise", "food", "rest"]},
                {"name": "Animals", "subtopics": ["pets", "wild", "babies", "habitats", "food", "life_cycles"]},
                {"name": "Plants", "subtopics": ["seeds", "growth", "parts", "needs", "habitats", "seasonal"]},
                {"name": "Weather", "subtopics": ["sun", "rain", "wind", "clouds", "seasons", "recording"]},
                {"name": "Materials", "subtopics": ["hard_soft", "rough_smooth", "bouncy", "absorbent", "floating", "magnetic"]},
            ]
        }
    },
    "primary": {
        "mathematics": {
            "topics": [
                {"name": "Number", "subtopics": ["place_value", "addition", "subtraction", "multiplication", "division", "fractions"]},
                {"name": "Geometry", "subtopics": ["2D_shapes", "3D_shapes", "angles", "symmetry", "coordinates", "transformations"]},
                {"name": "Measurement", "subtopics": ["length", "mass", "time", "money", "area", "perimeter"]},
                {"name": "Statistics", "subtopics": ["charts", "tables", "pictograms", "tally", "graphs", "averages"]},
                {"name": "Algebra", "subtopics": ["sequences", "input_output", "equations", "formulae", "functions", "graphs"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Reading", "subtopics": ["comprehension", "vocabulary", "inference", "genres", "poetry", "non_fiction"]},
                {"name": "Writing", "subtopics": ["narrative", "description", "instructions", "letters", "reports", "persuasion"]},
                {"name": "Grammar", "subtopics": ["punctuation", "spelling", "connectives", "tense", "paragraphs", "adjectives"]},
                {"name": "Speaking", "subtopics": ["dialogue", "presentation", "drama", " debate", "recitation", "conversation"]},
                {"name": "Spelling", "subtopics": ["common_words", "patterns", "rules", "homophones", "prefixes", "suffixes"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Biology", "subtopics": ["cells", "humans", "animals", "plants", "ecosystems", "food_chains"]},
                {"name": "Chemistry", "subtopics": ["materials", "states", "changes", " mixtures", "acids", "properties"]},
                {"name": "Physics", "subtopics": ["forces", "motion", "energy", "light", "sound", "electricity"]},
                {"name": "Earth Science", "subtopics": ["rocks", "fossils", "weather", "climate", "solar_system", "movement"]},
                {"name": "Scientific Method", "subtopics": ["hypotheses", "experiments", "evidence", "analysis", "conclusions", "reporting"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Digital Literacy", "subtopics": ["devices", "software", "files", "internet_safety", "keyboarding", "coding"]},
                {"name": "Algorithms", "subtopics": ["sequences", "loops", "conditions", "variables", "debugging", "design"]},
            ]
        }
    },
    "lower_secondary": {
        "mathematics": {
            "topics": [
                {"name": "Number", "subtopics": ["integers", "fractions", "decimals", "percentages", "ratios", "bounds"]},
                {"name": "Algebra", "subtopics": ["expressions", "equations", "inequalities", "graphs", "sequences", "formulae"]},
                {"name": "Geometry", "subtopics": ["angles", "polygons", "circles", "congruence", "similarity", "Pythagoras"]},
                {"name": "Statistics", "subtopics": ["collection", "representation", " averages", "spread", "probability", "hypothesis"]},
                {"name": "Trigonometry", "subtopics": ["sine", "cosine", "tangent", "rules", "graphs", "applications"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Literature", "subtopics": ["novels", "poetry", "drama", "analysis", "themes", "context"]},
                {"name": "Language", "subtopics": ["grammar", "vocabulary", "usage", "orthography", "discourse", "sociolinguistics"]},
                {"name": "Creative Writing", "subtopics": ["narrative", "descriptive", "dialogue", "Style", "Voice", "Revision"]},
                {"name": "Media", "subtopics": ["analysis", "representation", "bias", "techniques", "production", "evaluation"]},
                {"name": "Communication", "subtopics": ["speaking", "listening", "discussion", "debate", "presentation", "interview"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Biology", "subtopics": ["cells", "organisation", "nutrition", "transport", "bioenergetics", "homeostasis"]},
                {"name": "Chemistry", "subtopics": ["particles", "elements", "compounds", "reactions", "energy", "periodic_table"]},
                {"name": "Physics", "subtopics": ["forces", "energy", "waves", "electricity", "magnetism", "matter"]},
                {"name": "Earth Science", "subtopics": ["atmosphere", "hydrosphere", "lithosphere", "climate", "resources", "cycles"]},
                {"name": "Practical Science", "subtopics": ["measurement", "variables", "analysis", "evaluation", "report", "ethics"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Computer Systems", "subtopics": ["hardware", "software", "networks", "data_representation", "binary", "storage"]},
                {"name": "Algorithms", "subtopics": ["design", "efficiency", "searching", "sorting", "pseudo_code", "flowcharts"]},
                {"name": "Programming", "subtopics": ["syntax", "variables", "control", "functions", "arrays", "files"]},
                {"name": "Data Structures", "subtopics": ["arrays", "lists", "stacks", "queues", "trees", "graphs"]},
                {"name": "Databases", "subtopics": ["design", "tables", "queries", "forms", "reports", "SQL"]},
            ]
        }
    },
    "upper_secondary": {
        "mathematics": {
            "topics": [
                {"name": "Pure Math", "subtopics": ["algebra", "calculus", "trigonometry", "series", "vectors", "complex_numbers"]},
                {"name": "Mechanics", "subtopics": ["kinematics", "forces", "moments", "energy", "power", "momentum"]},
                {"name": "Statistics", "subtopics": ["probability", "distributions", "hypothesis_testing", "correlation", "regression", "estimation"]},
                {"name": "Decision Math", "subtopics": ["algorithms", "graph_theory", "linear_programming", "networks", "critical_path", "optimization"]},
                {"name": "Advanced Calculus", "subtopics": ["differentiation", "integration", "differential_equations", "series_expansion", "numerical_methods", "applications"]},
            ]
        },
        "english": {
            "topics": [
                {"name": "Literature", "subtopics": ["Shakespeare", "poetry", "prose", "drama", "critical_theory", "comparison"]},
                {"name": "Language Study", "subtopics": ["social_dialect", "register", "pragmatics", "discourse", "orthography", "history"]},
                {"name": "Creative Writing", "subtopics": ["fiction", "non_fiction", "poetry_drama", "reflection", "publication", "workshop"]},
                {"name": "rhetoric", "subtopics": ["argument", "persuasion", "style", "audience", "technique", "evaluation"]},
                {"name": "Media Studies", "subtopics": ["theory", "industry", "audience", "representation", "convergence", "digital_culture"]},
            ]
        },
        "science": {
            "topics": [
                {"name": "Physics", "subtopics": ["mechanics", "fields", "waves", "particles", "thermal_physics", "nuclear"]},
                {"name": "Chemistry", "subtopics": ["organic", "inorganic", "physical", "analysis", "kinetics", "equilibria"]},
                {"name": "Biology", "subtopics": ["cells", "biochemistry", "genetics", "ecology", "evolution", "physiology"]},
                {"name": "Environmental", "subtopics": ["pollution", "conservation", "climate", "resources", "sustainability", "biodiversity"]},
                {"name": "Research Methods", "subtopics": ["methodology", "statistics", "sampling", "qualitative", "quantitative", "peer_review"]},
            ]
        },
        "computing": {
            "topics": [
                {"name": "Systems", "subtopics": ["architecture", "networks", "operating_systems", "databases", "security", "virtualization"]},
                {"name": "Algorithms", "subtopics": ["complexity", "sorting", "searching", "graphs", "dynamic", "crypto"]},
                {"name": "Programming", "subtopics": ["OOP", "design_patterns", "testing", "documentation", "debugging", "version_control"]},
                {"name": "Data", "subtopics": ["structures", "compression", "encryption", "databases", "transactions", "big_data"]},
                {"name": "Web Tech", "subtopics": ["HTML_CSS", "JavaScript", "backend", "APIs", "security", "performance"]},
            ]
        }
    }
}

DAILY_SCHEDULE = {
    "early": {
        "start_time": "08:00",
        "end_time": "10:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "topic": "Numbers", "subtopic": "counting", "duration": 20},
            {"time": "08:25", "subject": "break", "duration": 5},
            {"time": "08:30", "subject": "english", "topic": "Speaking", "subtopic": "sounds", "duration": 20},
            {"time": "08:55", "subject": "break", "duration": 10},
            {"time": "09:05", "subject": "science", "topic": "Our Bodies", "subtopic": "parts", "duration": 20},
        ],
    },
    "primary": {
        "start_time": "08:00",
        "end_time": "11:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "topic": "Number", "subtopic": "place_value", "duration": 30},
            {"time": "08:35", "subject": "break", "duration": 5},
            {"time": "08:40", "subject": "english", "topic": "Reading", "subtopic": "comprehension", "duration": 30},
            {"time": "09:15", "subject": "break", "duration": 10},
            {"time": "09:25", "subject": "science", "topic": "Biology", "subtopic": "cells", "duration": 30},
        ],
    },
    "lower_secondary": {
        "start_time": "08:00",
        "end_time": "12:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "topic": "Number", "subtopic": "integers", "duration": 40},
            {"time": "08:45", "subject": "break", "duration": 5},
            {"time": "08:50", "subject": "english", "topic": "Literature", "subtopic": "novels", "duration": 40},
            {"time": "09:35", "subject": "break", "duration": 10},
            {"time": "09:45", "subject": "computing", "topic": "Computer Systems", "subtopic": "hardware", "duration": 40},
        ],
    },
    "upper_secondary": {
        "start_time": "08:00",
        "end_time": "12:00",
        "schedule": [
            {"time": "08:00", "subject": "mathematics", "topic": "Pure Math", "subtopic": "algebra", "duration": 40},
            {"time": "08:45", "subject": "break", "duration": 5},
            {"time": "08:50", "subject": "english", "topic": "Literature", "subtopic": "Shakespeare", "duration": 40},
            {"time": "09:35", "subject": "break", "duration": 10},
            {"time": "09:45", "subject": "computing", "topic": "Systems", "subtopic": "architecture", "duration": 40},
        ],
    },
}

LEVEL_LESSONS = {
    "early": {
        "total_topics": 1,
        "subtopics_per_topic": 1,
        "total_subtopics": 1,
        "lesson_duration": 80,
    },
    "primary": {
        "total_topics": 1,
        "subtopics_per_topic": 1,
        "total_subtopics": 1,
        "lesson_duration": 80,
    },
    "lower_secondary": {
        "total_topics": 1,
        "subtopics_per_topic": 1,
        "total_subtopics": 1,
        "lesson_duration": 80,
    },
    "upper_secondary": {
        "total_topics": 1,
        "subtopics_per_topic": 1,
        "total_subtopics": 1,
        "lesson_duration": 80,
    },
}

AI_MODE = "auto"

LLM_API_KEY = os.environ.get("OPENAI_API_KEY", os.environ.get("LLM_API_KEY", ""))
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-3.5-turbo")
LLM_API_URL = os.environ.get("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 500

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

WIFI_ENC_KEY = os.environ.get("WIFI_ENC_KEY", "camp-tutor-secure-key-2024")
MATCH_THRESHOLD = 0.5
SCORE_THRESHOLD = 0.6
MAX_HISTORY = 100