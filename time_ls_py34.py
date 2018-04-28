#!/usr/bin/python

import json
import sys
import os
import copy
import shutil
import glob
import subprocess
import time
import sqlite3
import datetime

def main():
    
    command = "ssh daint ls /scratch/daint/antonk"

    job_duration = -time.time()
    with open(os.devnull, "w") as fnull:
        proc = subprocess.Popen(command.split(), stdout = fnull, stderr = fnull)
        proc.wait()
    job_duration += time.time()
    
    print(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + " " + str(job_duration))

if __name__ == "__main__":
    main()


