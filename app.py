from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import os

app = Flask(__name__)

FONT_PATH = "DejaVuSans.ttf"
IMG_SIZE = (1080, 1080)
QUOTE_FONT_SIZE = 60
AUTHOR_FONT_SIZE = 36
PADDING = 50

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

def fetch_unsplash_image(query):
    if not UNSPLASH_ACCESS_KEY:
        raise ValueError("Unsplash access key not set")

    url = f"https://api.unsplash.com/photos/random?query={query}&orientation=squarish&client_id=9gibUN-0TPCXIOntuUC-Nr9dFdvi_NFKYzDwstKR6C0"
    res = requests.get(url)
    if res.status_code == 200:
        image_url = res.json()["urls"]["regular"]
        img_res = requests.get(image_url)
        return Image.open(BytesIO(img_res.content)).convert("RGB")
    else:
        raise ValueError("Failed to fetch image from Unsplash")

@app.route("/", methods=["GET"])
def home():
    return "Quote Generator with Unsplash is Live ✅"

@app.route("/generate", methods=["POST"])
def generate_image():
    try:
        data = request.get_json()
        text = data.get("text", "")
        author = data.get("author", "")
        keyword = data.get("keyword", "motivational background")

        if not text or not author:
            return jsonify({"error": "Missing text or author"}), 400

        try:
            bg = fetch_unsplash_image(keyword)
        except:
            bg = Image.new("RGB", IMG_SIZE, color=(30, 30, 30))

        bg = bg.resize(IMG_SIZE).filter(ImageFilter.GaussianBlur(radius=6))
        draw = ImageDraw.Draw(bg)

        try:
            quote_font = ImageFont.truetype(FONT_PATH, QUOTE_FONT_SIZE)
            author_font = ImageFont.truetype(FONT_PATH, AUTHOR_FONT_SIZE)
        except:
            quote_font = ImageFont.load_default()
            author_font = ImageFont.load_default()

        quote = f'"{text}"'
        author_text = f"- {author}"

        def wrap_text(text, font, max_width):
            lines = []
            words = text.split()
            while words:
                line = ""
                while words and draw.textlength(line + words[0], font=font) <= max_width:
                    line += words.pop(0) + " "
                lines.append(line.strip())
            return lines

        quote_lines = wrap_text(quote, quote_font, IMG_SIZE[0] - 2 * PADDING)
        total_quote_height = sum([draw.textbbox((0, 0), line, font=quote_font)[3] for line in quote_lines]) + 10 * len(quote_lines)
        author_size = draw.textbbox((0, 0), author_text, font=author_font)
        total_height = total_quote_height + (author_size[3] - author_size[1]) + 30

        y = (IMG_SIZE[1] - total_height) // 2

        for line in quote_lines:
            bbox = draw.textbbox((0, 0), line, font=quote_font)
            text_width = bbox[2] - bbox[0]
            x = (IMG_SIZE[0] - text_width) // 2
            draw.text((x + 2, y + 2), line, font=quote_font, fill="black")
            draw.text((x, y), line, font=quote_font, fill="white")
            y += bbox[3] + 10

        bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_width = bbox[2] - bbox[0]
        x = (IMG_SIZE[0] - author_width) // 2
        draw.text((x + 2, y + 2), author_text, font=author_font, fill="black")
        draw.text((x, y), author_text, font=author_font, fill="lightgray")

        output = BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)

        return send_file(output, mimetype="image/png")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
