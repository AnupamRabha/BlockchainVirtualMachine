# logging_config.py
import logging

def configure_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG
        format='%(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(),           # Output to console
            logging.FileHandler("debug.log")   # Save to debug.log
        ]
    )