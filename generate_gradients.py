#!/usr/bin/env python3

import argparse
import json
import math
import sys
from itertools import combinations
from PIL import Image, ImageColor, ImageDraw


def main():
    # Parse command-line arguments
    arg_parser = argparse.ArgumentParser(description='Draw square blocks of colors and gradients using all '
                                                     'combinations of pairs of those colors onto a transparent '
                                                     'background.',
                                         epilog='A square image will be produced, and its size will be automatically '
                                                'calculated as the smallest square that will fit the number of blocks '
                                                'generated, rounded up so its sides are a power of 2. Gradients are made '
                                                'between all combinations of pairs of colors.',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument('-f',
                            dest='image_file',
                            metavar='IMAGE_FILE',
                            type=check_image_format,
                            default='gradients.png',
                            help='Filename of the image to write.')
    arg_parser.add_argument('-s',
                            dest='block_size',
                            type=int,
                            default=64,
                            help='Size of square color blocks in pixels.')
    arg_parser.add_argument('-m',
                            nargs='?',
                            dest='map_file',
                            type=argparse.FileType('w'),
                            const='blocks.map',
                            help='Write a JSON file containing information about color blocks.')
    arg_parser.add_argument('colors',
                            nargs='+',
                            metavar='COLOR',
                            type=check_colors,
                            help='Base set of colors to use when generating gradients. Valid formats include hex '
                                 'code: #ffffff, RGB/RGBA tuple: rgb(0,0,0) / rgba(0,0,0,0), or any other '
                                 'format supported by Python Imaging Library (PIL).')
    args = arg_parser.parse_args()

    image_file = args.image_file
    map_file = args.map_file
    block_size = args.block_size
    colors = args.colors

    # Initialise sizes, etc
    base_colors = list(zip(colors, colors))
    gradients = list(combinations(colors, 2))
    min_width_blocks = int(math.ceil(math.sqrt(len(colors) + len(gradients))))
    canvas_size = int(math.pow(2, math.ceil(math.log(min_width_blocks * block_size, 2))))
    image = Image.new(size=(canvas_size, canvas_size),
                      mode='RGBA',
                      color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    block_map = {'block_map': []}

    base_x = 0
    base_y = 0

    # Draw base color blocks
    base_x, base_y = draw_gradients('Base Colors',
                                    draw,
                                    base_x,
                                    base_y,
                                    block_size,
                                    canvas_size,
                                    base_colors,
                                    block_map['block_map'])

    # Draw gradient blocks
    draw_gradients('Color Gradients',
                   draw,
                   base_x,
                   base_y,
                   block_size,
                   canvas_size,
                   gradients,
                   block_map['block_map'])

    # Write out image file
    try:
        image.save(image_file)
    except (IOError, ValueError) as e:
        print('ERROR: Could not write image to file {}: {}'.format(image_file.name,
                                                                   e))
        sys.exit(1)
    else:
        print('Wrote {0} x {0} pixel image to file {1}'.format(canvas_size,
                                                               image_file.name))

    # Write out block map file
    block_map_json = json.dumps(block_map, indent=4)
    try:
        map_file.write(block_map_json)
    except AttributeError:
        pass
    except IOError as e:
        print('ERROR: Could not block map to file {}: {}'.format(map_file.name,
                                                                 e))
        sys.exit(2)
    else:
        print('Wrote block map to file {1}'.format(canvas_size,
                                                   map_file.name))


def check_colors(value):
    '''Check whether a string is a valid PIL color specifier, and try common prefixes if not.'''

    try:
        ImageColor.getrgb(value)
    except ValueError:
        prefixes = ['#', 'rgb', 'rgba']
        for prefix in prefixes:
            prefixed_value = prefix + value
            try:
                ImageColor.getrgb(prefixed_value)
            except ValueError as e:
                continue
            else:
                return prefixed_value

        raise argparse.ArgumentTypeError("Unknown color specifier: '{}'. See help for valid formats.".format(value))


def check_image_format(value):
    '''Check whether it makes sense the write the type of file specified for output.'''

    out_file = argparse.FileType('wb')(value)
    image = Image.new(size=(1, 1),
                      mode='RGBA')
    try:
        image.save(out_file)
    except (ValueError, IOError) as e:
        raise argparse.ArgumentTypeError(str(e))

    out_file.seek(0)
    return out_file


def draw_gradients(name, draw, base_x, base_y, block_size, canvas_size, gradients, block_map):
    '''Draw blocks of gradients.'''

    print('Drawing {0}: {1} blocks of {2} x {2} pixels, starting from pixel {3}'.format(name,
                                                                                        len(gradients),
                                                                                        block_size,
                                                                                        (base_x, base_y)))
    block_map_entry = {'name': name,
                       'blocks': []}

    for gradient in gradients:
        start_color = ImageColor.getrgb(gradient[0])
        end_color = ImageColor.getrgb(gradient[1])

        # Calculate how much the color will change with each line drawn
        delta = tuple([float((end_channel - start_channel)) / float(block_size - 1)
                      for start_channel, end_channel
                      in zip(start_color, end_color)])

        # Draw a square block with a vertical gradient, line by line, starting from an X and Y coordinate. Since the
        # color delta is a float, the final color values will need to be quantised to integers
        for line in range(block_size):
            draw.line(xy=[(base_x, base_y + line), (base_x + block_size - 1, base_y + line)],
                      fill=tuple([int(round(float(start_channel) + delta_channel * line))
                                 for start_channel, delta_channel
                                 in zip(start_color, delta)]),
                      width=1)

        # Update the block map
        block_info = {
            'type': 'gradient',
            'origin': str((base_x, base_y)),
            'height': block_size,
            'width': block_size,
            'start_color': gradient[0],
            'end_color': gradient[1],
        }
        block_map_entry['blocks'].append(block_info)

        # Calculate the X and Y position of the next block of a given size on a canvas. If block would be drawn outwith
        # the canvas, advance to the nex line of blocks
        base_x = 0 if base_x + 2 * block_size > canvas_size else base_x + block_size
        base_y += block_size if base_x == 0 else 0

    block_map.append(block_map_entry)

    return base_x, base_y


if __name__ == '__main__':
    main()
