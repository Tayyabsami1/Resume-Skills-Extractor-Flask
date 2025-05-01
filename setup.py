import subprocess
import sys
import os

# Ensure spaCy model is installed during deployment
try:
    import spacy
    try:
        # Try to load the model
        spacy.load("en_core_web_sm")
        print("spaCy model already installed.")
    except:
        # If loading fails, install the model
        print("Installing spaCy English model...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        print("spaCy English model installed successfully.")
except Exception as e:
    print(f"Error with spaCy setup: {e}")
    print("Continuing anyway - app will use regex-only mode for skill extraction")