import numpy as np
import cv2
from collections import OrderedDict
import time


def arith_coding(fileVector, blockSize, probability):
    cumulative_p = {}
    cumulative_p_prev = {}
    tags = []

    cum_sum = 0.0
    for p in probability:
        cumulative_p[p] = (probability[p] + cum_sum)
        cumulative_p_prev[p] = cum_sum
        cum_sum += probability[p]

    idx = 0
    while(idx < len(fileVector)):
        l = 0.0
        u = 1.0
        for blockNum in range(blockSize):
            letter = fileVector[idx]
            new_l = l + (u-l) * cumulative_p_prev[letter]
            new_u = l + (u-l) * cumulative_p[letter]
            u = new_u
            l = new_l
            idx += 1
        tags.append((u+l)/2.0)

    return tags


img = cv2.imread('forest.jpg', cv2.IMREAD_GRAYSCALE)

dimensions = np.array([img.shape[0], img.shape[1]])  # height x width

img = img.flatten()
blockSize = 4

extraPixels = blockSize - (img.size % blockSize)
img = np.pad(img, (0, extraPixels), 'constant', constant_values=(0))

probability = {}

for pix in img:
    if pix in probability.keys():
        probability[pix] += 1
    else:
        probability[pix] = 1

sortedProbability = {}
for shade in range(256):
    if shade in probability.keys():
        sortedProbability[shade] = probability[shade]

probability = sortedProbability

for p in probability:
    probability[p] /= len(img)


probabilityVector = []

for shade in range(256):
    if shade in probability.keys():
        probabilityVector.append(probability[shade])
    else:
        probabilityVector.append(0)

probabilityVector = np.array(probabilityVector)
tags = np.array(arith_coding(img, blockSize, probability))

tags.tofile('tags.dat')
probabilityVector.tofile('probabilities.dat')
dimensions.tofile('dimensions.dat')
np.array([blockSize]).tofile('blocksize.dat')
