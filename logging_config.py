# logging_config.py
# Configures logging for the project

import logging

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )