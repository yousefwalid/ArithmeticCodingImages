# How to run?
1. Place the image as `test.jpg` in root folder
2. Run encoder `python encoder.py`
3. The encoded tags are stored in `./data/tags.dat` along with other information
4. To decode the tags run `python decoder.py`
5. The output is stored in `./output.jpg`

# Encoder arguments
The encoder can take two optional arguments:
1. `fileName` the name of the file specified to run, e.g. `test.jpg`
2. `blockSize` the block size of the compression. _defaults to 16_
