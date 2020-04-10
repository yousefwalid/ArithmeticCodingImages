import numpy as np
import cv2
import bisect
import pickle
import time


def convertBitStringToDecimal(bitString):
    num = 0
    idx = 1
    while (idx < len(bitString) + 1):
        num += 2**(-idx) * (bitString[idx-1] == '1')
        idx += 1
    return num


def arithmetic_decode(tags, blockSize, probability):
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
            if(l >= 0.0 and u < 0.5):
                l = 2 * l
                u = 2 * u
                tag = tag[1:]
            elif(l >= 0.5 and u <= 1.0):
                l = 2 * l - 1
                u = 2 * u - 1
                tag = tag[1:]
            elif(l >= 0.25 and u < 0.75):
                l = 2 * l - 0.5
                u = 2 * u - 0.5
                if(tag[0] == '0'):
                    tag = tag[2:]
                    tag = '0' + tag
                elif(tag[0] == '1'):
                    tag = tag[2:]
                    tag = '1' + tag
                else:
                    print('error')
            else:
                t = convertBitStringToDecimal(tag)
                delta = u-l
                new_t = (t-l)/delta
                letterIdx = numSymbols-1

                # letterIdx = bisect.bisect_right(
                #     cumulative_sum, new_t)-1

                for i in range(len(cumulative_sum)-1):
                    if(new_t >= cumulative_sum[i] and new_t < cumulative_sum[i+1]):
                        letterIdx = i
                        break

                outputSymbols.append(letterIdx)
                new_l = l + delta * cumulative_sum[letterIdx]
                new_u = min(l + delta * cumulative_sum[letterIdx+1], 1.0)
                l = new_l
                u = new_u
                blockNum += 1

    return outputSymbols


def decodeTags(tags):
    tagStringArray = []
    for tag in tags:
        tagString = ''
        for byte in tag:
            byteString = ''
            for i in range(8):
                byteString += chr((byte & 1) + ord('0'))
                byte >>= 1
            tagString += byteString[::-1]
        tagStringArray.append(tagString)
    return tagStringArray


with open('./data/tags.dat', 'rb') as x:
    tagsBytesArray = pickle.load(x)

tags = decodeTags(tagsBytesArray)

dimensions = np.fromfile('./data/dimensions.dat', dtype=int)
probabilityVector = np.fromfile('./data/probabilities.dat', dtype=float)
blockSize = (np.fromfile('./data/blocksize.dat', dtype=int)[0])

streamLength = len(tags) * blockSize

probability = []
indices = {}

for i in range(len(probabilityVector)):
    if(probabilityVector[i] > 0.0):
        indices[len(probability)] = i
        probability.append(probabilityVector[i])

start = time.process_time()

original_stream_indicies = arithmetic_decode(
    tags, blockSize, probability)

print(str(time.process_time() - start) + ' s')

original_stream = []

for idx in original_stream_indicies:
    original_stream.append(indices[idx])


original_image = np.array(original_stream[:(dimensions[0]*dimensions[1])], dtype=np.uint8).reshape(
    dimensions[0], dimensions[1])

cv2.imwrite('output.jpg', original_image)
