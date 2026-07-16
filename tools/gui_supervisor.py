import subprocess
import time
import sys

SCRIPT = 'jarvis_gui.py'

if __name__ == '__main__':
    while True:
        print('Starting GUI...')
        p = subprocess.Popen([sys.executable, SCRIPT])
        rc = p.wait()
        print(f'GUI exited with code {rc}')
        print('Restarting in 1s...')
        time.sleep(1)
