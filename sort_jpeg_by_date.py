import os
import hashlib
import EXIF

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


def main():
    for root, dirs, files in os.walk('.'):
        for f in files:
            # full name of the file
            fname = os.path.join(root,f)
    

if __name__ == "__main__":
    main()

