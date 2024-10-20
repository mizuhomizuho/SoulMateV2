import pathlib
import subprocess
import time
from datetime import datetime

if __name__ == '__main__':

    base = f'{pathlib.Path(__file__).parent.resolve()}/../..'

    cmd = (fr"cd {base} && .venv\Scripts\activate && py parser/step3/main.py")

    i = 0
    while True:
        try:
            print(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=20, shell=True)
        except subprocess.CalledProcessError as e:
            print('CalledProcessError', e.returncode, e)
            if i < 3:
                subprocess.Popen(f'py -c "import ctypes'
                     f'\nctypes.windll.user32.MessageBoxW(0, \'Check output\','
                     f' \'Err check output\', 0x1000)"')
            i += 1
        time.sleep(10)
        print('Restart')