import logging
from pathlib import Path
from datetime import datetime
import config.config

def test():
    print("LOG_DIR")

def runtime():
    print("hi")
    print(config.config.LOG_DIR)
