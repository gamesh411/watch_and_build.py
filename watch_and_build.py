#!/usr/bin/env python3

import time
import argparse
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, path_suffixes, build_script, run_script):
        self.build_script = build_script
        self.run_script = run_script
        self.path_suffixes = path_suffixes

    def on_any_event(self, event):
        if event.is_directory:
            return
        if event.event_type != "modified":
            return
        print(f"\nChange detected: {event.src_path}")
        if not any(event.src_path.endswith(suffix) for suffix in self.path_suffixes):
            print(
                f"Skipping {event.src_path} because it doesn't match any suffixes {self.path_suffixes}"
            )
            return
        self.run_build_and_test()

    def run_build_and_test(self):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Running build script...")

        try:
            # capture stderr as well because it's not always captured by the subprocess
            build_output = subprocess.run(
                [self.build_script],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            print("Build successful!")

            print(f"\n[{timestamp}] Running test script...")
            test_output = subprocess.run(
                [self.run_script],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            print(f"Test output:\n{test_output.stdout}")

        except subprocess.CalledProcessError as e:
            if e.cmd == self.build_script:
                print(f"Build failed. Error message:\n{e.stdout}")
            else:
                print(f"Test script failed. Error message:\n{e.stdout}")


def watch_directory(path, path_suffixes, build_script, run_script):
    event_handler = ChangeHandler(path_suffixes, build_script, run_script)
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
    parser = argparse.ArgumentParser(
        description="Watch a directory and run build/test scripts on changes."
    )
    parser.add_argument("path", help="Path to the directory to watch")
    parser.add_argument("build_script", help="Path to the build script")
    parser.add_argument("run_script", help="Path to the run/test script")
    parser.add_argument(
        "--suffixes",
        nargs="+",
        help="File suffixes to watch",
        default=[".cpp", ".h"],
        required=False,
    )

    args = parser.parse_args()

    print(f"Watching directory: {args.path}")
    print(f"Build script: {args.build_script}")
    print(f"Run script: {args.run_script}")
    print(f"Watching only suffixes: {args.suffixes}")
    print("Press Ctrl+C to stop...")

    watch_directory(args.path, args.suffixes, args.build_script, args.run_script)
