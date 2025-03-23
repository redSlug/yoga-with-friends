from datetime import datetime

from ppm.fonts import binary_font

LOOK_BACK_SECONDS = 60 * 60 * 12


def _draw_character(image, char_offset, char_data):
    char_width = 5
    char_height = 7
    width = len(image[0])
    height = len(image)
    skip_x = 1 + char_offset * (char_width + 1)
    top_margin = 4

    for row_index in range(char_height):
        char_row_bits = char_data[row_index]
        for col_index in range(char_width):
            pixel = (char_row_bits >> (4 - col_index)) & 1
            if pixel:
                img_x = skip_x + col_index
                img_y = row_index + top_margin
                if 0 <= img_x < width and 0 <= img_y < height:
                    image[img_y][img_x] = (255, 0, 0)  # red pixel
                else:
                    raise Exception("Pixel {} out of bounds".format(row_index))


LED_DISPLAY_WIDTH = 32
LED_DISPLAY_HEIGHT = 16


def create_text_image(
    filepath,
    text,
):
    image = [
        [(0, 0, 0) for _ in range(LED_DISPLAY_WIDTH)] for _ in range(LED_DISPLAY_HEIGHT)
    ]
    text = text[:5]
    for char_offset, char in enumerate(text):
        if char.upper() not in binary_font:
            raise Exception(f"Unknown character {char}")
        char_data = binary_font[char.upper()]
        _draw_character(image, char_offset, char_data)
    with open(filepath, "wb") as f:
        # PPM header
        f.write(b"P6\n32 16\n255\n")
        for row in image:
            for pixel in row:
                f.write(bytes(pixel))
        print(f"wrote image with text {text} to file: ", filepath)


def save_should_render(file_path, next_event):
    now = datetime.now()
    twelve_hours = LOOK_BACK_SECONDS
    time_until_next_class = next_event.timestamp - now.timestamp()
    should_render = time_until_next_class <= twelve_hours
    set_should_render(file_path, should_render)


def set_should_render(file_path: str, should_render: bool):
    print(f"should render={should_render}")
    with open(file_path, "w") as f:
        f.write(str(should_render))
