import sys
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    def on_any_event(self, event):
        # Process created files/directories
        if event.event_type == 'created':
            print(event.src_path)

if __name__ == "__main__":
    # set up logging object
    logging.basicConfig(level=logging.INFO,
                        format='%(message)s')
    
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