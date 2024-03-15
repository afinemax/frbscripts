#!/usr/bin/env python3

import curses
import os
import time
import subprocess

def get_disk_space(data_dir):
    # Get available disk space in GB
    result = subprocess.run(['df', '-k', data_dir], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').split('\n')[1].split()
    return float(output[3].replace(",", ".")) / 1024. / 1024.

def get_last_four_file_sizes(directory):
    # Get the file sizes of the last four files in the specified directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files = sorted(files, key=lambda f: os.path.getctime(os.path.join(directory, f)), reverse=True)[:3]
    files = sorted(files)  # Sort last four by name
    sizes = [os.path.getsize(os.path.join(directory, file)) for file in files]
    files += [""] * (3 - len(files))
    sizes += [0] * (3 - len(sizes))
    return files, sizes

def run_script():
    # Run the script and get the output and exit code
    result = subprocess.run(['/home_local/camrasdemo/frb/get_frb_from_pointing.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    output = result.stdout + result.stderr
    exit_code = result.returncode
    return output, exit_code

def get_data_dir():
    observe_vars_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'observe_vars.sh')
    with open(observe_vars_filename, "r") as f:
        for line in f:
            if line.strip().startswith("DATADIR"):
                data_dir = line.strip().split("=")[1].strip("'").strip('"')
    return data_dir
    #return '/data2/camrasdemo/frb/'

def main(stdscr):
    data_dir = get_data_dir()

    # Initialize last file sizes
    _, last_file_sizes = get_last_four_file_sizes(data_dir)

    curses.curs_set(0)
    curses.start_color()  # Initialize color pairs here

    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Red
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Yellow

    stdscr.clear()
    stdscr.nodelay(1)  # Make getch() non-blocking

    data_disk = data_dir.split("/")[1]

    while True:
        stdscr.clear()

        # Disk space
        disk_space = get_disk_space(data_dir)
        disk_space_color = curses.color_pair(1) if disk_space < 10 else curses.color_pair(2)
        stdscr.addstr(1, 1, f'Space on {data_disk}: {disk_space:.2f} GB', disk_space_color)

        # File sizes
        file_names, file_sizes = get_last_four_file_sizes(data_dir)
        stdscr.addstr(3, 1, 'Last four file sizes:', curses.color_pair(3))
        for i, (filename, size) in enumerate(zip(file_names, file_sizes)):
            size_color = curses.color_pair(1) if size == last_file_sizes[i] else curses.color_pair(2)
            size_mb = size / 1024. / 1024.
            if 'P' in filename:
                pad = ""
            else:
                pad = ""
            stdscr.addstr(4 + i, 3, f'{filename}{pad}: {size_mb: 5.0f} MB', size_color)

        last_file_sizes = file_sizes.copy()

        # Script output
        script_output, exit_code = run_script()
        script_color = curses.color_pair(1) if exit_code != 0 else curses.color_pair(2)
        stdscr.addstr(9, 1, 'FRB from pointing:', curses.color_pair(3))
        stdscr.addstr(10, 3, script_output, script_color)

        stdscr.addstr(12, 1, "Press q or Ctrl-C to exit dashboard")

        stdscr.refresh()

        # Get user input without blocking
        key = stdscr.getch()

        # Check if 'q' is pressed
        if key == ord('q'):
            break

        time.sleep(0.8)

if __name__ == '__main__':
    try:
        curses.wrapper(main)

    except KeyboardInterrupt:
        pass
