Chess Engine with AI and Hand Recognition Interface

Welcome to our advanced chess engine project! This application combines traditional chess gameplay with AI-driven opponent moves and an innovative hand-recognition interface for controlling the game. Developed using Python, Pygame, and Mediapipe, this project showcases AI implementation and human-computer interaction in a chess environment.

Features
🎮 Chess Gameplay
A fully functional chess board with all standard rules implemented, including:
Pawn promotion
Castling
En passant
Checkmate and stalemate detection
🧠 AI Opponent
AI opponent uses the Negamax algorithm with alpha-beta pruning to evaluate and choose moves.
The AI evaluates positions based on:
Material value of pieces
Positional advantages (e.g., knight position scores)
The AI responds dynamically to player moves.
✋ Hand Recognition Interface
Uses Mediapipe to enable hand-tracking for controlling the chess game:
Move the cursor with your index finger.
Click by bringing your thumb and index finger together.
Reset the board by showing a "peace sign" (index and middle fingers up).
Works seamlessly alongside traditional mouse input.
🚀 Multithreading and Optimization
Multithreading ensures smooth operation by running hand recognition and game logic simultaneously.
AI computation is performed in a separate process to maintain responsiveness.
Requirements
Python Version
Python 3.10 or higher
Dependencies
Install the required libraries using the following command:

bash
Copy code
pip install -r requirements.txt
Required Libraries:

pygame: For rendering the chess board and handling game interactions.
cv2 (OpenCV): For video capture and processing.
mediapipe: For hand recognition.
pyautogui: For simulating mouse movements and clicks.
tensorflow (optional): For any potential AI extensions in the future.
win32api (on Windows): For additional keyboard interaction.
Folder Structure
bash
Copy code
chess-engine-main/
├── Chess/
│   ├── ChessMain.py          # Main game script
│   ├── ChessEngine.py        # Game logic and rules
│   ├── SmartMoveFinder.py    # AI move generation
│   ├── images/               # Chess piece images (e.g., wp.png, wK.png, etc.)
│   │   ├── wp.png
│   │   ├── bp.png
│   │   ├── ...
└── requirements.txt          # Dependencies
Setup Instructions
Clone the Repository

bash
Copy code
git clone https://github.com/your-repository/chess-engine.git
cd chess-engine/Chess
Install Dependencies

bash
Copy code
pip install -r requirements.txt
Run the Game

bash
Copy code
python ChessMain.py
Ensure Images Are Correctly Located Verify that all chess piece images (e.g., wp.png, wK.png) are present in the images/ folder.

How to Play
Human vs AI

The player starts as White by default.
Moves are made by clicking on a piece and its target square.
The AI calculates and plays its move after yours.
Hand Recognition

Start the game, and the hand recognition module will run in parallel.
Control the cursor with your index finger.
Click by bringing the thumb and index finger together.
Reset the board with a "peace sign."
Game Controls

Undo Move: Press Z.
Reset Board: Press R.
Technical Details
AI Implementation
The AI uses:

Negamax algorithm with alpha-beta pruning:
Optimized to evaluate moves efficiently by cutting off unnecessary branches.
Heuristic Evaluation:
Material value of pieces.
Positional advantages (e.g., knight placement).
The AI operates at a search depth of 2 by default (adjustable).
Hand Recognition
Mediapipe is used for real-time hand tracking and gesture detection.
Gestures:
Cursor movement: Controlled by index finger.
Click: Detected by thumb-index pinch.
Reset: Peace sign gesture.
Multithreading
The hand recognition module runs as a separate thread.
AI computations are executed in a separate process using Python’s multiprocessing.
Known Issues
Hand Recognition

Hand tracking may lag slightly on low-spec systems.
Requires adequate lighting for consistent tracking.
AI Performance

The AI operates at a depth of 2 for balance between speed and strength. Increasing depth improves performance but slows response time.
File Paths

Ensure the working directory is set correctly for the images to load.
Future Improvements
AI Enhancements

Incorporate a deep learning model trained on a large chess dataset (e.g., Lichess).
Use TensorFlow or PyTorch for advanced AI.
Hand Recognition

Improve gesture recognition by introducing more robust filters.
Additional Features

Add multiplayer support (online or local).
Enhance the GUI for a more modern experience.
Contributors
[Amogh Pitale]: Core game logic, chess rules, and piece interactions.

[Shrey Sharma]: Hand recognition and gesture control.

[Ashish Arya]: AI implementation and optimizations.

[Abhijeet Sharma]: Multithreading and performance tuning.

[Tanish Kartik]: Overall integration and testing.
