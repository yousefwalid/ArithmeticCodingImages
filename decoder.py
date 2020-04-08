import numpy as np
import cv2
import bisect


def arithmetic_decode(tags, blockSize, probability, streamLength):
    numSymbols = len(probability)

    outputSymbols = []

    cumulative_sum = [0.0] * (numSymbols+1)

    for i in range(1, numSymbols+1):
        cumulative_sum[i] = cumulative_sum[i-1] + \
            probability[i-1]  # 1 based cumulative sum

    #cumulative_sum[numSymbols] = 1.0

    for tag in tags:
        for blockIdx in range(blockSize):
            charIdx = bisect.bisect_left(cumulative_sum, tag)-1
            # Now I have the index of the letter
            outputSymbols.append(charIdx)
            tag = (tag-cumulative_sum[charIdx])/probability[charIdx]

    return outputSymbols


tags = np.fromfile('tags.dat', dtype=float)
dimensions = np.fromfile('dimensions.dat', dtype=int)
probabilityVector = np.fromfile('probabilities.dat', dtype=float)
blockSize = (np.fromfile('blocksize.dat', dtype=int)[0])

streamLength = len(tags) * blockSize

probability = []
indices = {}

for i in range(len(probabilityVector)):
    if(probabilityVector[i] > 0.0):
        indices[len(probability)] = i
        probability.append(probabilityVector[i])

original_stream_indicies = arithmetic_decode(
    tags, blockSize, probability, streamLength)

original_stream = []

for idx in original_stream_indicies:
    original_stream.append(indices[idx])


original_image = np.array(original_stream[:(dimensions[0]*dimensions[1])], dtype=np.uint8).reshape(
    dimensions[0], dimensions[1])


cv2.imwrite('output.jpg', original_image)
