import numpy as np
import cv2
import bisect
import pickle

# def arithmetic_decode(tags, blockSize, probability, streamLength):
#     numSymbols = len(probability)

#     outputSymbols = []

#     cumulative_sum = [0.0] * (numSymbols+1)

#     for i in range(1, numSymbols+1):
#         cumulative_sum[i] = cumulative_sum[i-1] + \
#             probability[i-1]  # 1 based cumulative sum

#     cumulative_sum[numSymbols] = 1.0

#     for tag in tags:
#         for blockIdx in range(blockSize):
#             charIdx = bisect.bisect_left(cumulative_sum, tag)-1
#             # Now I have the index of the letter
#             outputSymbols.append(charIdx)
#             tag = min(0.99999999999999,
#                       (tag-cumulative_sum[charIdx])/probability[charIdx])

#     return outputSymbols


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
    tagIdx = 0
    for tag in tags:
        l = 0
        u = 1
        t = convertBitStringToDecimal(tag)
        blockNum = 0
        print(tagIdx)
        tagIdx += 1
        while(blockNum < blockSize):
            if(l >= 0 and u < 0.5):
                l = 2*l
                u = 2*u
                tag = tag[1:]
                t = convertBitStringToDecimal(tag)
            elif(l >= 0.5 and u <= 1.1):
                l = 2*l-1
                u = 2*u - 1
                tag = tag[1:]
                t = convertBitStringToDecimal(tag)
            # elif(l >= 0.25 and u < 0.75):
            #     l = 2 * (l - 0.25)
            #     u = 2 * (u - 0.25)
            #     tag = tag[2:]
            #     if(tag[:2] == '01'):
            #         tag = '0' + tag
            #     else:
            #         tag = '1' + tag
            #     t = convertBitStringToDecimal(tag)
            else:
                delta = (u-l)
                new_t = (t-l)/delta
                # charIdx = bisect.bisect_left(cumulative_sum, new_t)-1

                charIdx = numSymbols-1
                for i in range(len(cumulative_sum)-1):
                    if(new_t >= cumulative_sum[i] and new_t < cumulative_sum[i+1]):
                        charIdx = i
                        break
                outputSymbols.append(charIdx)
                new_l = l + delta * cumulative_sum[charIdx]
                new_u = min(
                    l + delta * cumulative_sum[charIdx+1], 1.0)
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
