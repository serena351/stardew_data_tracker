from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
FILEPATH = os.getenv("FILEPATH")
PARENT_DIR = os.path.dirname(FILEPATH)

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = None

    def on_modified(self, event): # run extract.py every time save file is updated
        if not event.is_directory and event.src_path == FILEPATH:
            current_time = time.time()
            if self.last_modified and self.last_modified[0] == event.src_path and current_time - self.last_modified[1] < 2:
                return # ignore duplicate events
            self.last_modified = (event.src_path, current_time)
            print("Save file has been updated")
            
            # Run ETL script (extract.py)
            try:
                subprocess.run(["python", "extract.py"], check=True)
                print("ETL script executed successfully")
            except subprocess.CalledProcessError as e: 
                print(f"Error while running extract.py: {e}")
            
observer = Observer() # initialise observer
observer.schedule(Handler(), FILEPATH) # watch parent directory of file
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    
observer.join()