# How to run?

1. Place the image in root folder
2. Run encoder `python encoder.py`
3. Fill in the required inputs
4. The encoded tags are stored in `./data/tags.dat` along with other information
5. To decode the tags run `python decoder.py`
6. The output is stored in `./output.jpg`

# Encoder arguments

The encoder can take two inputs:

1. The file name, e.g. `test.jpg`
2. The block size, e.g. `16`

- This encoder uses encoding with scaling, it outputs a byte array and not a float np array, this is why it doesn't have a datatype input
- This implementation can handle high blocksizes (tested up to 1024 but it can handle more), however as the blockSize increases, it will take more time
- It will not be efficient at low blockSizes like 16
