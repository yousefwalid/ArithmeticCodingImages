import numpy as np
import cv2
import bisect
import pickle


def convertBitStringToDecimal(bitString):
    num = 0
    idx = 1
    while (idx < len(bitString) + 1):
        num += 2**(-idx) * (bitString[idx-1] == '1')
        idx += 1
    return num


def arithmetic_decode(tags, blockSize, probability, streamLength):
    numSymbols = len(probability)

    outputSymbols = []

    cumulative_sum = [0.0] * (numSymbols+1)

    for i in range(1, numSymbols+1):
        cumulative_sum[i] = cumulative_sum[i-1] + \
            probability[i-1]  # 1 based cumulative sum

    cumulative_sum[numSymbols] = 1.0
    for tag in tags:
        l = 0.0
        u = 1.0
        blockNum = 0
        while(blockNum < blockSize):
            if(l >= 0 and u < 0.5):
                l = 2 * l
                u = 2 * u
                tag = tag[1:]
            elif(l >= 0.5 and u <= 1.1):
                l = 2 * l - 1
                u = 2 * u - 1
                tag = tag[1:]
            # elif(l >= 0.25 and u < 0.75):
            #     l = 2 * l - 0.5
            #     u = 2 * u - 0.5
            #     if(tag[:2] == '01'):
            #         tag = tag[2:]
            #         tag = '0' + tag
            #     else:
            #         tag = tag[2:]
            #         tag = '1' + tag
            else:
                t = convertBitStringToDecimal(tag)
                delta = u-l
                new_t = (t-l)/delta
                letterIdx = 0

                letterIdx = bisect.bisect_left(cumulative_sum, new_t)-1

                # for i in range(len(cumulative_sum)-1):
                #     if(new_t >= cumulative_sum[i] and new_t < cumulative_sum[i+1]):
                #         letterIdx = i
                #         break
                outputSymbols.append(letterIdx)
                new_l = l + delta * cumulative_sum[letterIdx]
                new_u = min(l + delta * cumulative_sum[letterIdx+1], 1.0)
                l = new_l
                u = new_u
                blockNum += 1

    return outputSymbols


# tags = np.fromfile('tags.dat', dtype=float)
with open("test.txt", "rb") as fp:   # Unpickling
    tags = pickle.load(fp)

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
