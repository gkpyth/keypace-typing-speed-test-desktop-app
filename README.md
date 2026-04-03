# KeyPace

A desktop typing speed test app built with Python and CustomTkinter; part of personal bootcamp projects portfolio.

## Features
- Real-time WPM and accuracy tracking
- Character-by-character highlighting (green for correct, red for incorrect)
- Line-by-line text scrolling — always see what's coming
- Selectable test durations: 1, 2, 3, 4, or 5 minutes
- Timer starts on first printable keystroke
- Backspace support with accurate accuracy recalculation
- Support auto-scrolling to the next line when the end of the second line is reached
- Keeps one line above visible for easy reference
- Persistent leaderboard (top 10 scores saved locally)
- Dark and light mode toggle
- Refresh button to load a new passage before starting

## Requirements
- Python 3.10+
- customtkinter

## Installation

1. Clone the repository:
```
git clone https://github.com/gkpyth/keypace.git
cd keypace
```

2. Install dependencies:
```
pip install customtkinter
```

## How to Run
```
python main.py
```

## How to Use
- Select a test duration (default: 1 minute)
- Click **Start** to load a passage
- If unhappy with the passage, click **Refresh** to get a new one
- Begin typing — the timer starts on your first keystroke
- Characters turn green if correct, red if incorrect
- Backspace to correct mistakes
- When time runs out, your results are displayed automatically
- Enter your initials and save your score to the leaderboard

## Project Structure
```
keypace/
├── main.py         # App entry point
├── ui.py           # All CustomTkinter UI code and app logic
├── logic.py        # WPM/accuracy calculations and leaderboard management
├── texts.py        # Pool of text passages for the typing test
├── scores.json     # Local leaderboard storage (auto-generated)
└── .gitignore
```

## Leaderboard
Scores are saved locally to `scores.json`. The leaderboard stores the top 10 scores ranked by WPM, each entry including initials, WPM, accuracy, and time used.

## Limitations
- Desktop only — not a web app
- Font rendering for the passage text is optimized for Windows (Segoe UI)

## Author
Ghaleb Khadra