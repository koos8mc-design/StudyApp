# -*- coding: utf-8 -*-
"""
Voortgang opslaan/laden tussen sessies.
Werkt zowel als los script (main.py) als gebundeld in een .exe (PyInstaller).
Slaat een klein JSON-bestand op naast het programma: voortgang.json
"""
import json
import os
import sys


def _get_progress_path():
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "voortgang.json")


def word_key(pair):
    """Maakt een unieke sleutel voor een (grieks, nederlands) paar."""
    return f"{pair[0]}\u2016{pair[1]}"


def load_progress():
    path = _get_progress_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_progress(data):
    path = _get_progress_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass  # opslaan mislukt (bv. geen schrijfrechten) - app blijft gewoon werken


def register_result(progress, pair, was_correct):
    """Werkt de progress-dict bij voor een gegeven woordpaar."""
    key = word_key(pair)
    entry = progress.get(key, {"correct": 0, "wrong": 0})
    if was_correct:
        entry["correct"] += 1
    else:
        entry["wrong"] += 1
    progress[key] = entry
    return progress


def wrong_count(progress, pair):
    return progress.get(word_key(pair), {}).get("wrong", 0)


def difficult_words_count(progress, pool):
    """Aantal woorden uit pool waarbij ooit vaker fout dan goed geantwoord is."""
    n = 0
    for pair in pool:
        entry = progress.get(word_key(pair))
        if entry and entry.get("wrong", 0) > 0 and entry.get("wrong", 0) >= entry.get("correct", 0):
            n += 1
    return n
