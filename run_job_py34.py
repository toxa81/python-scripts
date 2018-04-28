#!/usr/bin/python
#SBATCH --job-name="test_gemm"
#SBATCH --time=0:20:00
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --account=csstaff
#SBATCH --reservation=fallenotb

import json
import sys
import os
import copy
import shutil
import glob
import subprocess
import time
import sqlite3
def main():
    
    if len(sys.argv) < 2:
        print("Usage: run_job_py34.py command [options]")
        sys.exit(0)
    
    num_ranks = int(os.environ["SLURM_NPROCS"])

    new_env = copy.deepcopy(os.environ)
    new_env["OMP_NUM_THREADS"] = "8"
    new_env["OMP_NESTED"] = "false"
    new_env["MKL_NUM_THREADS"] = "8"
    new_env["MKL_DYNAMIC"] = "false"
    new_env["CRAY_CUDA_MPS"] = "0"
    new_env["MPICH_RDMA_ENABLED_CUDA"] = "1"
    new_env["MPICH_NO_GPU_DIRECT"] = "1"
    new_env["CRAY_LIBSCI_ACC_MODE"] = "1"
    new_env["MPICH_MAX_THREAD_SAFETY"] = "multiple"

    aprun_command = "aprun -n " + str(num_ranks) + " -N1 -d8 -cc none"

    job_duration = -time.time()
    path = "./"
    proc = subprocess.Popen(aprun_command.split() + sys.argv[1:], cwd=path, env=new_env)
    proc.wait()
    job_duration += time.time()

    conn = sqlite3.connect("/users/antonk/DB/jobs.sql3")
    c = conn.cursor()

    result = c.execute("SELECT max(job_id) FROM jobs_list").fetchone()
    
    jobid = int(result[0]) + 1
    job_name = os.environ["SLURM_JOB_NAME"]
    job_command = aprun_command + " " + " ".join(sys.argv[2:])
    c.execute("INSERT INTO jobs_list(job_id, job_name, command, num_ranks, job_duration) \
               VALUES(" + str(jobid) + ", '" + job_name + "', '" + job_command + "', " + str(num_ranks) + ", " + str(int(job_duration)) + ")")

    
    fname = "slurm-" + os.environ["SLURM_JOB_ID"] + ".out"
    fcontent = open(fname).read()
    fcontent = fcontent.replace("'", "''")
    
    sql_statement = "INSERT INTO jobs_output_files VALUES(" + str(jobid) + ", '" + fname + "', '" + fcontent + "')"
    c.execute(sql_statement)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()


