# uv_gradients

```
usage: generate_gradients.py [-h] [-f IMAGE_FILE] [-s BLOCK_SIZE]
                             [-m [MAP_FILE]]
                             COLOR [COLOR ...]

Draw square blocks of colors and gradients using all combinations of pairs of
those colors onto a transparent background.

positional arguments:
  COLOR          Base set of colors to use when generating gradients. Valid
                 formats include hex code: #ffffff, RGB/RGBA tuple: rgb(0,0,0)
                 / rgba(0,0,0,0), or any other format supported by Python
                 Imaging Library (PIL).

optional arguments:
  -h, --help     show this help message and exit
  -f IMAGE_FILE  Filename of the image to write. (default: gradients.png)
  -s BLOCK_SIZE  Size of square color blocks in pixels. (default: 64)
  -m [MAP_FILE]  Write a JSON file containing information about color blocks.
                 (default: None)

A square image will be produced, and its size will be automatically calculated
as the smallest square that will fit the number of blocks generated, rounded
up so its sides are a power of 2. Gradients are made between all combinations
of pairs of colors.
```

# Example

```
./generate_gradients.py 8DB6C7 C1B38E D1C6BF CA9F92 F9CD97 E3D9B0 B1C27A B2E289 51C0BF 59ADD0 7095E1 9FA3E3 C993D4 DB8DB2 F1C3D0
```

![Example output](https://github.com/Evoludo/uv_gradients/raw/master/example/gradients.png "Example output")
