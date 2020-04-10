import numpy as np
import cv2
import time
import pickle


def get_binaryStr_within_range(l, u):
    i = 1
    num = 0
    binaryStr = ''
    while (not(num >= l and num < u)):
        decimal_pnt = 2**(-i)
        new_decimal = num + decimal_pnt
        if(new_decimal > u):
            binaryStr += '0'
        else:
            binaryStr += '1'
            num = new_decimal
        i += 1
    return binaryStr


def arith_coding(fileVector, blockSize, probability):
    cumulative_p = {}
    cumulative_p_prev = {}
    tags = []

    last_prob = 0
    for p in probability:
        cumulative_p_prev[p] = last_prob
        cumulative_p[p] = last_prob + probability[p]
        last_prob = cumulative_p[p]

    idx = 0
    while(idx < len(fileVector)):
        l = 0.0
        u = 1.0
        tag = ''
        blockNum = 0
        c = 0
        while (blockNum < blockSize):
            if(l >= 0 and u < 0.5):
                l = 2 * l
                u = 2 * u
                tag += '0'
                for ic in range(c):
                    tag += '1'
                c = 0
            elif (l >= 0.5 and u <= 1.0):
                l = 2 * l - 1
                u = 2 * u - 1
                tag += '1'
                for ic in range(c):
                    tag += '0'
                c = 0
            elif(l >= 0.25 and u < 0.75):
                l = 2 * l - 0.5
                u = 2 * u - 0.5
                c += 1
            else:
                if(blockNum == blockSize-1):
                    letter = fileVector[idx]
                    new_l = l + (u-l) * cumulative_p_prev[letter]
                    new_u = l + (u-l) * cumulative_p[letter]
                    extra_bits = get_binaryStr_within_range(new_l, new_u)
                    tag += extra_bits
                else:
                    letter = fileVector[idx]
                    delta = u-l
                    new_l = l + delta * cumulative_p_prev[letter]
                    new_u = min(
                        l + delta * cumulative_p[letter], 1.0)
                    l = new_l
                    u = new_u
                idx += 1
                blockNum += 1
        tags.append(tag)
    return tags


def bitstring_to_bytes(s):
    # pad s to make it divisble by 8
    numBits = 8 - len(s) % 8
    s += ('0' * numBits)
    return bytes(int(s[i: i + 8], 2)
                 for i in range(0, len(s), 8))  # convert s to bytes


def encodeTags(tags):
    bytesArray = []
    for tag in tags:
        bytesArray.append(bitstring_to_bytes(tag))
    return bytesArray


img = cv2.imread('shoma32.jpg', cv2.IMREAD_GRAYSCALE)

dimensions = np.array([img.shape[0], img.shape[1]])  # height x width

img = img.flatten()
blockSize = 16

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

probabilityVector = np.array(probabilityVector, dtype=float)

start = time.process_time()

tags = arith_coding(img, blockSize, sortedProbability)

print(str(time.process_time() - start) + ' s')

tagsBytesArray = encodeTags(tags)

with open('./data/tags.dat', 'wb') as x:
    pickle.dump(tagsBytesArray, x)

probabilityVector.tofile('./data/probabilities.dat')
dimensions.tofile('./data/dimensions.dat')
np.array([blockSize]).tofile('./data/blocksize.dat')
