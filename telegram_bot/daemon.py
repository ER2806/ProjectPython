import os
import subprocess
import time

processname = 'main_serv'

# старт таймера

while True:
    tmp = os.popen("ps -Af").read()
    proccount = tmp.count(processname)
    if proccount == 0:
        print(proccount, 'Start ', processname)
        subprocess.call(["python3", "main_serv.py"])
    else:
        print("running")
    time.sleep(600)
