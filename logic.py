import random
import json
from texts import TEXT_SAMPLES

def get_random_text():
    test_text = random.choice(TEXT_SAMPLES)
    return test_text

def calculate_wpm(chars_typed, seconds_elapsed):
    """Returns the WPM (Words Per Minute) count."""
    minutes = seconds_elapsed / 60
    wpm = (chars_typed / 5) / minutes
    return wpm

def load_leaderboard():
    with open("scores.json", "r") as file:
        data = json.load(file)
    return data["leaderboard"]

def save_score(initials, wpm, accuracy, duration):
    leaderboard = load_leaderboard()
    score = {
        "initials": initials,
        "wpm": wpm,
        "accuracy": accuracy,
        "duration": duration,
    }
    leaderboard.append(score)
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x["wpm"], reverse=True)
    sliced_leaderboard = sorted_leaderboard[:10]
    data = {"leaderboard": sliced_leaderboard}

    with open("scores.json", "w") as file:
        json.dump(data, file, indent=4)
