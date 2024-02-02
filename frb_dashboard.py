#!/usr/bin/env python3

import curses
import os
import time
import subprocess

def get_disk_space():
    # Get available disk space in GB
    result = subprocess.run(['df', '-h', '/data2'], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').split('\n')[1].split()
    return float(output[3].replace("Gi", "").replace('G', '').replace(",", "."))

def get_last_three_file_sizes(directory):
    # Get the file sizes of the last three files in the specified directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    files = sorted(files, key=lambda f: os.path.getctime(os.path.join(directory, f)), reverse=True)[:3]
    files = sorted(files)  # Sort last three by name
    sizes = [os.path.getsize(os.path.join(directory, file)) for file in files]
    return files, sizes

def run_script():
    # Run the script and get the output and exit code
    result = subprocess.run(['/home_local/camrasdemo/frb/get_frb_from_pointing.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    output = result.stdout
    exit_code = result.returncode
    return output, exit_code

def main(stdscr):
    # Initialize last file sizes
    _, last_file_sizes = get_last_three_file_sizes('/data2/camrasdemo/frb')

    curses.curs_set(0)
    curses.start_color()  # Initialize color pairs here

    # Initialize color pairs
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Red
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Yellow

    stdscr.clear()
    stdscr.nodelay(1)  # Make getch() non-blocking

    while True:
        stdscr.clear()

        # Disk space
        disk_space = get_disk_space()
        disk_space_color = curses.color_pair(1) if disk_space < 10 else curses.color_pair(2)
        stdscr.addstr(1, 1, f'Space on /data2: {disk_space:.2f} GB', disk_space_color)

        # File sizes
        file_names, file_sizes = get_last_three_file_sizes('/data2/camrasdemo/frb/')
        stdscr.addstr(3, 1, 'Last three file sizes:', curses.color_pair(3))
        for i, (filename, size) in enumerate(zip(file_names, file_sizes)):
            size_color = curses.color_pair(1) if size == last_file_sizes[i] else curses.color_pair(2)
            size_mb = size / 1024. / 1024.
            stdscr.addstr(4 + i, 3, f'{filename}: {size_mb:.0f} MB, {last_file_sizes[i]/1024.:.0f}', size_color)

        last_file_sizes = file_sizes.copy()

        # Script output
        script_output, exit_code = run_script()
        script_color = curses.color_pair(1) if exit_code != 0 else curses.color_pair(2)
        stdscr.addstr(9, 1, 'FRB from pointing:', curses.color_pair(3))
        stdscr.addstr(10, 3, script_output, script_color)

        stdscr.refresh()

        # Get user input without blocking
        key = stdscr.getch()

        # Check if 'q' is pressed
        if key == ord('q'):
            break

        time.sleep(5)

if __name__ == '__main__':
    try:
        curses.wrapper(main)

    except KeyboardInterrupt:
        pass
