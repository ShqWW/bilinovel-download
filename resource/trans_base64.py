from PIL import Image
import base64
from resource.logo import logo_base64
import io

# # 从Base64编码数据中获取图像数据
# image_bytes = base64.b64decode(logo_base64)

# # 将图像数据解码为Image对象
# image = Image.open(io.BytesIO(image_bytes))

# # 显示图像
# image.show()


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")

image_path = "resource/book.png "
base64_string = image_to_base64(image_path)
print(base64_string)