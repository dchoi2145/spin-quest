import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from open_root_file import is_file_still_writing

class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Process created files/directories
        if event.event_type == 'created':
            created_path = event.src_path
            
            # check if path is directory
            if (os.path.isdir(created_path)):
                print("Created new directory: " + created_path)
            else:
                print("Created new file: " + created_path)

                # check if file is file is done uploading
                print("Checking if file is closed...")
                while is_file_still_writing(created_path, 0.1):
                    print("File still writing...")
                print("File is closed!")

if __name__ == "__main__":
    # choose path to watch
    path = sys.argv[1] if len(sys.argv) > 1 else '.'

    # event handler
    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    # main loop
    try:    
        while observer.is_alive():
            observer.join(1)
    finally:    
        observer.stop()
        observer.join()