import os
import sys

argv = sys.argv
argc = len(sys.argv)

print(argc, argv)

itterations = 10
if(argc == 2):
    itterations = int(argv[1])

print(itterations)
for i in range(itterations):
    # print(i)
    os.chdir("./project2")
    os.system("python ./variant5.py")
    os.chdir("..")