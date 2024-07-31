#!/usr/bin/env python3

import argparse
import diff_match_patch
import difflib
import subprocess
import time
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, path_suffixes, build_script, run_script):
        self.build_script = build_script
        self.run_script = run_script
        self.path_suffixes = path_suffixes
        self.last_test_output = None

    def on_closed(self, event):
        if event.is_directory:
            return
        print(f"\nChange detected: {event.src_path}")
        if not any(event.src_path.endswith(suffix) for suffix in self.path_suffixes):
            print(
                f"Skipping {event.src_path} because it doesn't match any suffixes {self.path_suffixes}"
            )
            return
        self.run_build_and_test()

    def highlight_line_diff(self, last_test_output, current_test_output):
        if last_test_output is None:
            return current_test_output

        diff = difflib.ndiff(
            last_test_output.splitlines(keepends=True),
            current_test_output.splitlines(keepends=True),
        )

        colored_diff = []
        for line in diff:
            if line.startswith("+ "):
                colored_diff.append(f"\033[92m{line[2:]}\033[0m")
            elif line.startswith("- "):
                colored_diff.append(f"\033[91m{line[2:]}\033[0m")
            elif line.startswith("? "):
                pass
            else:
                colored_diff.append(line)
        return "".join(colored_diff)

    def highlight_char_diff(self, last_test_output, current_test_output):
        if last_test_output is None:
            return current_test_output

        dmp = diff_match_patch.diff_match_patch()
        diffs = dmp.diff_main(last_test_output, current_test_output)
        dmp.diff_cleanupSemantic(diffs)

        colored_diff = []
        for diff in diffs:
            if diff[0] == dmp.DIFF_INSERT:
                colored_diff.append(f"\033[92m{diff[1]}\033[0m")
            elif diff[0] == dmp.DIFF_DELETE:
                colored_diff.append(f"\033[91m{diff[1]}\033[0m")
            else:
                colored_diff.append(diff[1])
        return "".join(colored_diff)

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
            print(
                f"Test output:\n{self.highlight_char_diff(self.last_test_output, test_output.stdout)}"
            )
            self.last_test_output = test_output.stdout

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

    print("Press Ctrl+C to trigger a build manually...")

    double_interrupted = False
    while not double_interrupted:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            try:
                print("Rebuilding...")
                event_handler.run_build_and_test()
                print("Press Ctrl+C again withing 1 second to stop...", end="")
                sys.stdout.flush()
                time.sleep(1)
                print("reset")
            except KeyboardInterrupt:
                double_interrupted = True
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

    watch_directory(args.path, args.suffixes, args.build_script, args.run_script)
