import sys
import numpy as np

argv = sys.argv
argc = len(sys.argv)

# print(argc, argv)

currentWeights = np.load('weights.npy')

numWeights = len(currentWeights)

if(argc == 1):
    newWeights = np.array([1.0] * numWeights)
else:
    newWeights = currentWeights

for i in range(argc - 1):
    if(i >= numWeights):
        break
    # print(i, argv[i+1])
    newWeights[i] = argv[i+1]

print(f"New Weights: {newWeights}")

np.save('weights.npy', newWeights)

    
