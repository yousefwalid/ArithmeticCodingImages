import numpy as np
import cv2
from collections import OrderedDict


def arithmetic_decode(tags, blockSize, probability, streamLength):

    original_stream = []
    idx = 0
    while(idx < streamLength):
        l = 0
        u = 1
        tag = tags[int(idx/blockSize)]
        for blockNum in range(blockSize):
            cumulative_p = 0
            for letter in probability:
                new_l = l + (u-l) * cumulative_p
                new_u = l + (u-l) * (cumulative_p + probability[letter])
                cumulative_p += probability[letter]
                if (tag > new_l and tag < new_u):
                    l = new_l
                    u = new_u
                    original_stream.append(letter)
                    idx += 1
                    break
    return original_stream


tags = np.fromfile('tags.dat', dtype=float)
dimensions = np.fromfile('dimensions.dat', dtype=int)
probabilityVector = np.fromfile('probabilities.dat', dtype=float)
blockSize = (np.fromfile('blocksize.dat', dtype=int)[0])

streamLength = dimensions[0] * dimensions[1]

probability = OrderedDict()

for i in range(len(probabilityVector)):
    if(probabilityVector[i] > 0.0):
        probability[i] = probabilityVector[i]

original_stream = arithmetic_decode(tags, blockSize, probability, streamLength)

original_image = np.array(original_stream[:streamLength], dtype=np.uint8).reshape(
    dimensions[0], dimensions[1])

# cv2.imshow('image', original_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

cv2.imwrite('output.jpg', original_image)
