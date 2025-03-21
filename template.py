import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')


backend = "backend"
frontend = "frontend"
list_of_files = [
    ".github/workflows/.gitkeep",
    f"{backend}/main.py",
    f"{backend}/utils.py",
    f"{frontend}/App.js",
    f"{backend}/file_processing.py",
    f"{backend}/tempdir.py",
    f"{backend}/config.py",
    f"{backend}/.env",
    f"{backend}/app.py",
    f"{backend}/questions.py",
    f"{backend}/redis_client.py",
    f"{backend}/agent_test.py",
    ".dockerignore",
    "docker-compose.yml",
]


for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory:{filedir} for the file {filename}")

    
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath,'w') as f:
            pass
            logging.info(f"Creating empty file: {filepath}")


    
    else:
        logging.info(f"{filename} is already exists")