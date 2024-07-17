import time
import argparse
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, build_script, run_script):
        self.build_script = build_script
        self.run_script = run_script

    def on_any_event(self, event):
        if event.is_directory:
            return
        print(f"\nChange detected: {event.src_path}")
        self.run_build_and_test()

    def run_build_and_test(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Running build script...")
        
        try:
            build_output = subprocess.run(
                [self.build_script], 
                check=True, 
                capture_output=True, 
                text=True
            )
            print("Build successful!")
            
            print(f"\n[{timestamp}] Running test script...")
            test_output = subprocess.run(
                [self.run_script], 
                check=True, 
                capture_output=True, 
                text=True
            )
            print(f"Test output:\n{test_output.stdout}")
        
        except subprocess.CalledProcessError as e:
            if e.cmd == self.build_script:
                print(f"Build failed. Error message:\n{e.stderr}")
            else:
                print(f"Test script failed. Error message:\n{e.stderr}")

def watch_directory(path, build_script, run_script):
    event_handler = ChangeHandler(build_script, run_script)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch a directory and run build/test scripts on changes.")
    parser.add_argument("path", help="Path to the directory to watch")
    parser.add_argument("build_script", help="Path to the build script")
    parser.add_argument("run_script", help="Path to the run/test script")
    
    args = parser.parse_args()
    
    print(f"Watching directory: {args.path}")
    print(f"Build script: {args.build_script}")
    print(f"Run script: {args.run_script}")
    print("Press Ctrl+C to stop...")
    
    watch_directory(args.path, args.build_script, args.run_script)
