import math
import subprocess


def main():
    cores_map = {'daint-mc'  : 36,
                 'daint-gpu' : 12,
                 'tave'      : 64}

    constrain_map = {'daint-mc'  : 'mc', 
                     'daint-gpu' : 'gpu',
                     'tave'      : 'cache,quad'}

    sirius_code_map = {'daint-mc'  : '/users/antonk/codes/pw.sirius.cpu.mkl.x',
                       'daint-gpu' : '/users/antonk/codes/pw.sirius.gpu.mkl.x',
                       'tave'      : '/users/antonk/codes/pw.sirius.knl.x'}
    
    input_file = 'water-Pt.in'

    code = 'pw-sirius' #'pw-sirius' # 'pw-module' or 'pw-sirius'
    platform = 'tave' # 'daint-gpu' or 'daint-mc' or 'tave'

    npool = 2
    #num_diag_nodes = [4, 9, 16]
    num_diag_nodes = [9, 16, 25]
    # number of threads per rank
    num_threads = [1,2,4,8,16]
    #number of cores per node
    num_cores = cores_map[platform]

    # find possible combinations of ranks and threads for a single node
    node_conf = []
    for t in num_threads:
        n = num_cores / t
        if n * t == num_cores:
            node_conf.append((n, t))

    for Nd in num_diag_nodes:
        for c in node_conf:
            n = int(math.sqrt(c[0] * Nd + 0.1))
            if (n * n == c[0] * Nd):
                #print("ndiag nodes: %i, %iR:%iT"%(Nd, c[0] * Nd, c[1]))
                num_nodes = npool * Nd
                # number of nodes times number of ranks per node
                num_ranks = num_nodes * c[0]
                # string id
                strid = "%inodes_%iR_%iT_%indiag_%inpool"%(num_nodes, num_ranks, c[1], Nd * c[0], npool)
                fname = "run_%s.slrm"%(strid)
                with open(fname, "w") as f:
                    f.write("#!/bin/bash -l\n")
                    f.write("#SBATCH --job-name=\"QE\"\n")
                    f.write("#SBATCH --nodes=%i\n"%(num_nodes))
                    f.write("#SBATCH --time=00:20:00\n")
                    f.write("#SBATCH --account=csstaff\n")
                    f.write("#SBATCH -C %s\n"%(constrain_map[platform]))

                    f.write("export KMP_AFFINITY='granularity=fine,compact,1'\n")
                    #export MPICH_MAX_THREAD_SAFETY=multiple
                    
                    if code == 'pw-module':
                        f.write("module load daint-mc\n")
                        f.write("module load QuantumESPRESSO/6.1.0-CrayIntel-17.08\n")
                
                    f.write("export OMP_NUM_THREADS=%i\n"%(c[1]))
                    f.write("export MKL_NUM_THREADS=%i\n"%(c[1]))
                    #f.write("export COMPLEX_ELPA_KERNEL=COMPLEX_ELPA_KERNEL_GENERIC\n")

                    outfile = "%s-%s-%s.out"%(code, platform, strid)
                    if code == 'pw-module':
                        f.write("srun -n %i -c %i --hint=nomultithread --unbuffered %s -i %s -npool %i -ndiag %i > %s\n"%(num_ranks, c[1], 'pw.x',                                                                        input_file, npool, c[0] * Nd, outfile))
                    elif code == 'pw-sirius':
                        f.write("srun -n %i -c %i --hint=nomultithread --unbuffered %s -i %s -npool %i -ndiag %i -sirius -sirius_cfg /users/antonk/codes/config.json > %s\n"%(num_ranks, c[1], sirius_code_map[platform], input_file, npool, c[0] * Nd, outfile))
                    elif code == 'pw-master':
                        f.write("srun -n %i -c %i --hint=nomultithread --unbuffered %s -i %s -npool %i -ndiag %i > %s\n"%(num_ranks, c[1], '/users/antonk/codes/pw.master.x',                                             input_file, npool, c[0] * Nd, outfile))
                    else:
                        raise ValueError('unknown code')

                p = subprocess.Popen(["sbatch", fname])
                p.wait()

if __name__ == "__main__":
    main()

