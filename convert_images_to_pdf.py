# Convert images to pdf
#
# Based on:
# - https://datatofish.com/images-to-pdf-python/#:~:text=%20Steps%20to%20Convert%20Images%20to%20PDF%20using,the%20image%20to%20PDF%20using%20Python%20More%20
# - https://stackoverflow.com/questions/48278187/argparse-what-is-the-difference-between-sys-argv1-and-args-input
#
# python convert_images_to_pdf.py data/image_1.jpeg data/image_2.jpeg data/image_3.jpeg


import sys
from PIL import Image


OUTPUT_FILENAME = 'merge.pdf'


if __name__ == '__main__':
    #print('Number of arguments:', len(sys.argv), 'arguments')
    #print('Argument list:', str(sys.argv))

    images = sys.argv[1:] 

    #print(images)

    pil_images = []

    try:
        for image in images:
            pil_images.append(Image.open(image))

        convert_pil_images = []

        for pil_image in pil_images:
            convert_pil_images.append(pil_image.convert('RGB'))

        image_list = convert_pil_images[1:] 

        convert_pil_images[0].save(OUTPUT_FILENAME, save_all = True, append_images = image_list)

    except Exception as e:
        print('Error: {0}\nException message: {1}'.format(type(e).__name__, e))