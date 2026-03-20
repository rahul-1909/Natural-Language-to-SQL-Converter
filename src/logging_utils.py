import logging
import os
from datetime import datetime

def setup_logging():
    try:
        log_folder = "logs"
        os.makedirs(log_folder, exist_ok=True)

        log_file = os.path.join(log_folder, f"session_{datetime.now().strftime('%Y%m%d')}.log")
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(log_file, mode='a'),
                logging.StreamHandler()
            ],
            force=True
        )
        logging.info("Logging system initialized")
    except Exception as e:
        print(f"Critical logging error: {str(e)}")
        raise

def log_message(message: str):
    logging.info(message)