#!/usr/bin/env python
#SBATCH --job-name="job_submit.py"
#SBATCH --time=0:02:00
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --account=csstaff

import json
import sys
import os
import copy
import shutil
import glob
import subprocess
import time
import psycopg2

tag = "test_hloc__17_12_2015"
threads_per_rank = 8
ranks_per_node = 1

env = {}
env["OMP_NUM_THREADS"] = str(threads_per_rank)
env["OMP_NESTED"] = "false"
env["MKL_NUM_THREADS"] = str(threads_per_rank)
env["MKL_DYNAMIC"] = "false"
#env["CRAY_CUDA_MPS"] = "0"
#env["MPICH_RDMA_ENABLED_CUDA"] = "1"
#env["MPICH_NO_GPU_DIRECT"] = "1"
#env["CRAY_LIBSCI_ACC_MODE"] = "1"
#env["MPICH_MAX_THREAD_SAFETY"] = "multiple"

def main():

    if len(sys.argv) < 2:
        print("Usage: %s command [options]"%sys.argv[0])
        sys.exit(0)

    new_env = copy.deepcopy(os.environ)
    for key in env:
        new_env[key] = env[key]

    num_nodes = int(os.environ["SLURM_NNODES"])
    num_ranks = ranks_per_node * num_nodes
    slurm_job_id = os.environ["SLURM_JOB_ID"]

    aprun_command = "aprun -n %i -N %i -d %i -cc none"%(num_ranks, ranks_per_node, threads_per_rank)
    job_command = aprun_command + " " + " ".join(sys.argv[1:])

#    job_duration = -time.time()
    path = "./"
    proc = subprocess.Popen(job_command.split(), cwd=path, env=new_env)
    proc.wait()
#    job_duration += time.time()

    fcontent = open("slurm-%s.out"%slurm_job_id).read()
#    fcontent = fcontent.replace("'", "''")

    sql_insert_command = "INSERT INTO jobs(slurm_job_id, name, tag, num_nodes, environment, command, output) \
        VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')"%(slurm_job_id, os.environ["SLURM_JOB_NAME"], tag, \
        os.environ["SLURM_NNODES"], json.dumps(env), job_command, fcontent)

    #print(sql_insert_command)

    conn = psycopg2.connect(database='postgres', user='postgres', password='Impostgres', host='aktest', port='5432')
    conn.cursor().execute(sql_insert_command)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()


