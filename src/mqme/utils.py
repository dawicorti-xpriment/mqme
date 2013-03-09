import Image

IMAGE_RATIO = 2
MAX_WIDTH = 400

def get_resized_image(path):
    image = Image.open(path)
    width, height = image.size
    return image.resize((width / IMAGE_RATIO, height / IMAGE_RATIO), Image.ANTIALIAS)

def get_cropped_images(path):
    image = Image.open(path)
    images = []
    width, height = image.size
    count = width / MAX_WIDTH
    for index in range(count):
        sub_image = image.crop((
            index * MAX_WIDTH, 0, index * MAX_WIDTH + MAX_WIDTH, height
        ))
        sub_image.load()
        images.append(sub_image)

    return images