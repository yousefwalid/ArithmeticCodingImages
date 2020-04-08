import numpy as np
import cv2
import bisect

# def arithmetic_decode(tags, blockSize, probability, streamLength):

# cum_sum = 0.0
# for p in probability:
#     cumulative_p[p] = (probability[p] + cum_sum)
#     cumulative_p_prev[p] = cum_sum
#     cum_sum += probability[p]

# original_stream = []
# idx = 0
# while(idx < streamLength):
#     l = 0.0
#     u = 1.0
#     tag = tags[int(idx/blockSize)]

#     for blockNum in range(blockSize):
#         for letter in probability:
#             new_l = l + (u-l) * cumulative_p_prev[letter]
#             new_u = l + (u-l) * cumulative_p[letter]
#             if ((tag >= new_l) and (tag < new_u)):
#                 l = new_l
#                 u = new_u
#                 original_stream.append(letter)
#                 idx += 1
#                 break
# return original_stream


def arithmetic_decode(tags, blockSize, probability, streamLength):
    numSymbols = len(probability)

    outputSymbols = []

    cumulative_sum = [0] * (numSymbols+1)

    for i in range(1, numSymbols+1):
        cumulative_sum[i] = cumulative_sum[i-1] + \
            probability[i-1]  # 1 based cumulative sum

    cumulative_sum[256] = 1.0

    for tag in tags:
        for blockIdx in range(blockSize):
            charIdx = bisect.bisect_left(cumulative_sum, tag)-1
            # Now I have the index of the letter
            outputSymbols.append(charIdx)
            l = cumulative_sum[charIdx]
            u = cumulative_sum[charIdx+1]
            delta = u-l
            tag = (tag-l)/delta

    return outputSymbols


tags = np.fromfile('tags.dat')
dimensions = np.fromfile('dimensions.dat', dtype=int)
probabilityVector = np.fromfile('probabilities.dat')
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

# cv2.imshow('image', original_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

cv2.imwrite('output.jpg', original_image)
