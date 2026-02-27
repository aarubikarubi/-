from PIL import Image, ImageDraw

def create_icon():
    image = Image.new('RGB', (256, 256), color=(30, 30, 30))
    d = ImageDraw.Draw(image)
    # 枠と緑色の四角形を描画
    d.rectangle(
        [(32, 32), (224, 224)],
        fill=(100, 200, 100),
        outline=(200, 255, 200),
        width=8
    )
    # テキスト等ではなく図でシンプルに表現
    image.save("icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("icon.ico created.")

if __name__ == "__main__":
    create_icon()
