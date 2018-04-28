import os
import hashlib

#def callback(arg, directory, files):
#    for file in files:
#        print os.path.join(directory, file), repr(arg)
#
#os.path.walk(".", callback, "secret message")


#def md5hash(fname):
#    md5 = hashlib.md5()
#    with open(fname, "rb") as f:
#        while True:
#            data = f.read(128 * md5.block_size)
#            if not data: break
#            md5.update(data)
#    return md5.digest()

def compare_two_files(fname1, fname2):

    md5_1 = hashlib.md5()
    md5_2 = hashlib.md5()

    with open(fname1, "rb") as f1:
        with open(fname2, "rb") as f2:
            while True:
                data1 = f1.read(1024)
                data2 = f2.read(1024)
                if not data1: break
                md5_1.update(data1)
                md5_2.update(data2)

                if md5_1.digest() != md5_2.digest():
                    return False

    return True

def inspect_group_of_files(fsize, files):

    duplicate_size = 0
    eq_files = {}

    # groups of files
    fgroup = [0 for i in range(len(files))]
    
    igroup = 0
    for i in range(len(files)):
        # if this file was not checked
        if fgroup[i] == 0:
            igroup += 1
            # this file receives a new group
            fgroup[i] = igroup

            eq_files.setdefault(igroup, []).append(files[i])
            # inspect other files
            for j in range(i + 1, len(files)):
                if fgroup[j] == 0 and compare_two_files(files[i], files[j]):
                    fgroup[j] = fgroup[i]
                    eq_files.setdefault(igroup, []).append(files[j])
    
    for key in eq_files:
        if (len(eq_files[key]) > 1):
            duplicate_size += fsize * (len(eq_files[key]) - 1)
            print("=== duplicate files of size: %.4f M ==="%(fsize / 1024 / 1024))
            for f in eq_files[key]:
                print("  " + f)
    
    return duplicate_size

def main():
    nfiles_tot = 0
    equal_size_files = {}
    for root, dirs, files in os.walk('.'):
        for f in files:
            # full name of the file
            fname = os.path.join(root,f)
    
            # size of the file
            size = os.path.getsize(fname)

            # append file to the list of files with the same sizes
            equal_size_files.setdefault(size, []).append(fname)

            nfiles_tot = nfiles_tot + 1
    
    duplicate_size = 0
    nfiles = 0
    for key in equal_size_files:
        if len(equal_size_files[key]) > 1 and key != 0: 
            nfiles += len(equal_size_files[key]) 
            duplicate_size += inspect_group_of_files(key, equal_size_files[key])
    
    print("total size of duplicates: %.4f M"%(duplicate_size / 1024 / 1024));
    print("%i files inspected"%nfiles)
    print("%i files listed"%nfiles_tot)

if __name__ == "__main__":
    main()

