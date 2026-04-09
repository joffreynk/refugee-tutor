# Camp Tutor - Mobile AI Learning Robot

A mobile AI learning robot for educational purposes, built with Raspberry Pi and ESP32.

## Features

- **Wake Word Detection**: Activates on "Camp Tutor" phrase
- **Language-Aware Tutoring**: Detects and adapts to learner's language
- **Multi-language Support**: English, Mandarin Chinese, Hindi, Spanish, Standard Arabic, French, Bengali, Portuguese, Russian, Indonesian, Urdu, German, Japanese, Nigerian Pidgin, Egyptian Arabic, Marathi, Vietnamese, Telugu, Turkish, Cantonese
- **Progress Tracking**: Tracks student progress over time
- **Homework Generation**: Creates personalized homework assignments
- **Assessment Engine**: Generates quizzes and evaluates responses
- **TensorFlow Lite**: On-device AI inference for edge deployment
- **Visual Feedback**: Nokia LCD 5110 display
- **Safe Movement**: LOOK->MEASURE->DECIDE->MOVE protocol

## Quick Start

```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the robot
cd pi
python3 main.py --interactive
```

## Hardware

- Raspberry Pi 3 B+ (master controller)
- ESP32 (REX controller)
- Pi Camera v2
- USB Microphone
- Nokia LCD 5110
- Servo motors, ultrasonic sensor

## Documentation

See `docs/` folder for detailed documentation:
- `SPEC.md` - System architecture and specifications
- `SETUP.md` - Hardware wiring and installation guide

## License

MIT
