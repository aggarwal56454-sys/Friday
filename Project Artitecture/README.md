AI-Powered Virtual Touchscreen System 🚀

An advanced, production-grade computer vision system that transforms any non-touch laptop or desktop screen into an interactive gesture-controlled interface using only a standard webcam. No cloud APIs, no external hardware—runs entirely locally with high-performance real-time hand-tracking.

Developed with a futuristic, cyberpunk-style desktop control center built in PyQt5, this system maps physical hand movements into fluid, hardware-level operating system controls.

🌟 Key Features

Real-Time 21-Landmark Hand Tracking: Uses an optimized local pipeline to track hand movements at 30-60 FPS with low latency.

Futuristic Cyberpunk Dashboard: A polished PyQt5 glassmorphic desktop control panel containing live vision overlays, dynamic stats (Engine FPS, Tracking Mode, Target Coordinates), and configuration options.

EMA (Exponential Moving Average) Smoothing: Advanced math-based cursor stabilization that eliminates webcam jitter, offering smooth trackpad-like navigation.

Dynamic Deadzone Mapping: Maps a comfortable bounding box in physical space to your full screen resolution so you never have to awkwardly stretch your arm.

Interactive Gesture Engine:

Move Cursor: Hold up only your Index Finger.

Left Click / Drag: Pinch your Thumb and Index finger together.

Right Click: Pinch your Thumb and Middle finger together (stabilized with state-cooldowns to prevent button spamming).

Lock Cursor (Sleep Mode): Make a closed Fist to safely release control.

Unlock Cursor: Present an Open Palm to resume control.

CPU Optimization: Background multi-threading and micro-sleep queues prevent 100% CPU lockups, allowing the system to run seamlessly on mid-range laptops.

🏗️ System Architecture

Project Artitecture/
│
├── dashboard.py             # Main Entry Point (PyQt5 Cyberpunk GUI)
├── main.py                  # CLI / OpenCV Headless HUD Fallback
├── requirements.txt         # Project Dependencies
├── .gitignore               # Excludes virtual environments and cache
│
└── src/
    ├── __init__.py          # Package Initialization
    ├── camera.py            # Multi-threaded Video Stream Handler
    ├── tracker.py           # MediaPipe Hands Wrapper & Coordinate Extractor
    ├── gestures.py          # State Machine & Mathematical Finger Distance Solver
    ├── controller.py        # Pynput Hardware Controller & Smoothing Engine
    └── utils.py             # Coordinate Mapper & Geometry Math


🛠️ Tech Stack & Requirements

Language: Python 3.11 (Recommended standard for AI/MediaPipe stability)

GUI Framework: PyQt5

Computer Vision / AI: OpenCV, MediaPipe

Inputs / Mapping: NumPy, Pynput

💾 Installation Guide

1. Prerequisites (Crucial)

This project uses Python 3.11. Ensure you do not use experimental versions like Python 3.14, as MediaPipe’s compiled C++ engine is optimized specifically for stable releases (3.10 - 3.12).

2. Setup Virtual Environment

Clone this project or navigate to your project directory, then run:

# Create a fresh Python 3.11 environment
python -m venv .venv

# Activate the environment (Windows PowerShell)
.venv\Scripts\Activate.ps1


3. Install Dependencies

pip install -r requirements.txt


🎮 How to Run

Launch the fully-interactive PyQt5 control dashboard:

python dashboard.py


For the simpler, direct window overlay version without the GUI dashboard:

python main.py


🕹️ Gesture Cheat Sheet

Gesture

Real-world Movement

OS Action

Move Cursor

Only index finger pointing up

Smooth pointer movement

Left Click / Drag

Pinch Thumb + Index Finger

Left Mouse Press / Drag

Right Click

Pinch Thumb + Middle Finger

Single Right Click

Lock Tracking

Closed Fist

Freezes pointer (Safe to drop arm)

Unlock Tracking

Open Palm (5 fingers extended)

Resumes active movement tracking

⚡ Performance Optimization & Troubleshooting

Webcam lagging or screen freezing? The dashboard is heavily optimized with self.msleep(10) to yield system processes back to Windows. Ensure no background apps (Teams, Zoom, Discord) are fighting for your webcam.

Clicking feels too stiff? You can increase the click sensitivity by editing the pinch_threshold inside src/gestures.py (Default: 50).

Jittery cursor? Drag the Cursor Smoothing slider to the left inside the dashboard. This increases the mathematical dampening.