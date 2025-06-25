import os
from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_image():
    data = request.json
    text = data.get('text', '')
    author = data.get('author', '')
    
    # Create image
    img = Image.new('RGB', (1080, 1080), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("DejaVuSans.ttf", 42)
    caption = f'"{text}"\n\n— {author}'
    lines = textwrap.wrap(caption, width=40)

    y_text = 400
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        draw.text(((1080 - width) / 2, y_text), line, font=font, fill=(0, 0, 0))
        y_text += height + 10

    # Return image
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

@app.route('/')
def hello():
    return "Image Generator API is running!"

# 👇 Bind to 0.0.0.0 and PORT from env
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
