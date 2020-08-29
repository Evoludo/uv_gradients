#!/usr/bin/env python

import math
from itertools import combinations
from PIL import Image, ImageColor, ImageDraw


def main():
    block_size = 64
    colors = ['#8DB6C7',
              '#C1B38E',
              '#D1C6BF',
              '#CA9F92',
              '#F9CD97',
              '#E3D9B0',
              '#B1C27A',
              '#B2E289',
              '#51C0BF',
              '#59ADD0',
              '#7095E1',
              '#9FA3E3',
              '#C993D4',
              '#DB8DB2',
              '#F1C3D0']

    gradients = list(combinations(colors, 2))
    min_blocks = int(math.ceil(math.sqrt(len(gradients) + len(colors))))
    canvas_size = int(math.pow(2, math.ceil(math.log(min_blocks * block_size, 2))))
    image = Image.new(size=(canvas_size, canvas_size),
                      mode='RGBA',
                      color=(0, 0, 0, 0))

    base_x = 0
    base_y = 0

    for color in colors:
        draw_block(image,
                   base_x,
                   base_y,
                   block_size,
                   lambda line: color)
        base_x, base_y = next_block(base_x,
                                    base_y,
                                    block_size,
                                    canvas_size)

    for gradient in gradients:
        start_color = ImageColor.getrgb(gradient[0])
        end_color = ImageColor.getrgb(gradient[1])
        delta = tuple([float((end_channel - start_channel)) / float(block_size - 1)
                      for start_channel, end_channel
                      in zip(start_color, end_color)])

        draw_block(image,
                   base_x,
                   base_y,
                   block_size,
                   lambda line: 'rgb' + str(tuple([int(round(float(start_channel) + delta_channel * line))
                                                   for start_channel, delta_channel
                                                   in zip(start_color, delta)])))

        base_x, base_y = next_block(base_x,
                                    base_y,
                                    block_size,
                                    canvas_size)

    image.save('gradients.png')


def draw_block(image,
               base_x,
               base_y,
               block_size,
               fill_func):

    draw = ImageDraw.Draw(image)

    for line in range(block_size):
        draw.line(xy=[(base_x, base_y + line), (base_x + block_size - 1, base_y + line)],
                  fill=fill_func(line),
                  width=1)


def next_block(base_x,
               base_y,
               block_size,
               canvas_size):
    base_x = 0 if base_x + 2 * block_size > canvas_size else base_x + block_size
    base_y += block_size if base_x == 0 else 0
    return base_x, base_y


if __name__ == '__main__':
    main()
