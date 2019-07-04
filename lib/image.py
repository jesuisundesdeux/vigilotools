#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image, ImageColor, ImageDraw, ImageFont


def make_collage(issues, img_text_options, width, init_height):
    # Source: https://github.com/delimitry/collage_maker
    """
    Make a collage image with a width equal to `width` from `images`
    """
    if not issues:
        print('No images for collage found!')
        return False

    margin_size = 2
    # run until a suitable arrangement of images is found
    while True:
        # copy images to images_list
        issues_list = issues[:]
        coefs_lines = []
        images_line = []
        x_pos = 0
        while issues_list:
            # get first image and resize to `init_height`
            issue = issues_list.pop(0)
            img_path = f"/tmp/{issue['token']}.png"
            img = Image.open(img_path)
            img.thumbnail((width, init_height))

            # when `x` will go beyond the `width`, start the next line
            if x_pos > width:
                coefs_lines.append((float(x_pos) / width, images_line))
                images_line = []
                x_pos = 0
            x_pos += img.size[0] + margin_size
            images_line.append(issue)

        # finally add the last line with images
        coefs_lines.append((float(x_pos) / width, images_line))

        # compact the lines, by reducing the `init_height`, if any with one or less images
        if len(coefs_lines) <= 1:
            break
        if any(map(lambda c: len(c[1]) <= 1, coefs_lines)):
            # reduce `init_height`
            init_height -= 10
        else:
            break

    # get output height
    out_height = 0
    for coef, imgs_line in coefs_lines:
        if imgs_line:
            out_height += int(init_height / coef) + margin_size
    if not out_height:
        print('Height of collage could not be 0!')
        return False

    collage_image = Image.new(
        'RGB', (width, int(out_height)), (35, 35, 35))
    # put images to the collage
    y_pos = 0
    for coef, imgs_line in coefs_lines:
        if imgs_line:
            x_pos = 0
            for issue in imgs_line:
                img_path = f"/tmp/{issue['token']}.png"
                img = Image.open(img_path)
                # if need to enlarge an image - use `resize`, otherwise use `thumbnail`, it's faster
                k = (init_height / coef) / img.size[1]
                if k > 1:
                    img = img.resize(
                        (int(img.size[0] * k), int(img.size[1] * k)), Image.ANTIALIAS)
                else:
                    img.thumbnail(
                        (int(width / coef), int(init_height / coef)), Image.ANTIALIAS)

                d = ImageDraw.Draw(img)
                font = ImageFont.truetype(
                    f'Cantarell-Regular.otf', img_text_options['size'])

                twidth, theight = d.textsize(
                    img_text_options['text'].format(**issue), font=font)

                if img_text_options['background'] != "":
                    color = ImageColor.getrgb(
                        img_text_options['background'])
                    d.rectangle(
                        ((0, img.size[1]-theight-(2*img_text_options['margin'])), (img.size[0], img.size[1])), fill=color, outline=color, width=8)

                if twidth < img.size[0]:
                    color = ImageColor.getrgb(
                        img_text_options['color'])
                    d.text(((img.size[0]-twidth)/2, img.size[1]-theight-img_text_options['margin']), img_text_options['text'].format(**issue),
                           font=font, fill=color)

                if collage_image:
                    collage_image.paste(img, (int(x_pos), int(y_pos)))
                x_pos += img.size[0] + margin_size
            y_pos += int(init_height / coef) + margin_size
    return collage_image
