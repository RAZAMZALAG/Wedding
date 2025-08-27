from flask import Blueprint, request, jsonify
from logger_config import get_logger
import os
import google.generativeai as genai
from models import Item, Category
import re
from urllib.parse import quote

ai_bp = Blueprint("ai", __name__)
logger = get_logger(__name__)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

REFUSAL_MESSAGES = {
    "he": "סליחה, אני יכולה לעזור רק בשאלות על רכישת מוצרים וחפצים לחתונות מהקטלוג שלנו במתחם Wedding Dreams.",
    "en": "Sorry, I can only help with questions about buying wedding equipment and items from our catalog.",
    "ar": "عذرًا، يمكنني المساعدة فقط في الأسئلة حول شراء معدات وأدوات الزفاف من كتالوجنا.",
    "ru": "Извините, я могу помочь только с вопросами о покупке свадебного оборудования из нашего каталога.",
}

def get_catalog_summary():
    items = Item.query.filter_by(hidden=False).all()
    category_map = {}
    for item in items:
        cat = item.category or "Uncategorized"
        category_map.setdefault(cat, []).append(item.name)
    all_categories = [cat.name for cat in Category.query.all()]
    summary = ""
    for cat in all_categories:
        summary += f"{cat}:\n"
        for name in category_map.get(cat, []):
            summary += f"- {name}\n"
    return summary

def linkify_item_names(reply, item_names):
    # Only link the first found item name (usually the relevant one)
    for name in item_names:
        # Use word boundaries to avoid partial matches
        pattern = r'(?<!\w)(' + re.escape(name) + r')(?!\w)'
        url = f"/catalog?search={quote(name)}"
        # Replace only the first occurrence
        reply, count = re.subn(pattern, f"[\\1]({url})", reply, count=1)
        if count > 0:
            break
    return reply

@ai_bp.route("/ask", methods=["POST"])
def ask_ai():
    data = request.get_json()
    user_message = data.get("message", "")
    lang = data.get("lang", "en")  # Default to English if not provided
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    catalog_summary = get_catalog_summary()

    system_prompt = (
        "You are an assistant for a wedding planning store.\n"
        "Here is the current wedding equipment catalog, organized by category:\n"
        f"{catalog_summary}\n"
        "Only answer questions about buying, ordering, or finding wedding items in the equipment catalog above. "
        "If the user asks anything unrelated (for example, recipes, general advice, or anything not about weddings/catalog), "
        f"respond with: '{REFUSAL_MESSAGES.get(lang, REFUSAL_MESSAGES['en'])}'"
    )

    try:
        response = model.generate_content([system_prompt, user_message])
        gemini_reply = response.text
        
        logger.info(f"AI assistant query processed", extra={'extra_data': {
            'language': lang,
            'user_message_length': len(user_message),
            'response_length': len(gemini_reply)
        }})
        
        return jsonify({"reply": gemini_reply})
    except Exception as e:
        logger.error(f"Gemini API error in ask endpoint", exc_info=True, extra={'extra_data': {
            'language': lang,
            'user_message_length': len(user_message) if user_message else 0
        }})
        return jsonify({"error": "Gemini API error"}), 400

@ai_bp.route("/ask-image", methods=["POST"])
def ask_image():
    lang = request.form.get("lang", "en")
    file = request.files.get("image")
    user_text = request.form.get("text", "")  # <-- get user text if provided

    if not file:
        return jsonify({"error": "No image provided"}), 400
    if file.mimetype not in ["image/jpeg", "image/png", "image/webp"]:
        return jsonify({"error": "Unsupported image type"}), 400
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > 10 * 1024 * 1024:
        return jsonify({"error": "Image too large"}), 400

    items = Item.query.filter_by(hidden=False).all()
    item_names = [item.name for item in items]
    catalog_summary = get_catalog_summary()

    system_prompt = (
        "You are an assistant for a wedding planning store.\n"
        "Here is the current wedding equipment catalog, organized by category (item names are in Hebrew):\n"
        f"{catalog_summary}\n"
        f"The user's language is: {lang} or the language he typed in. Respond in this language.\n"
        "You will receive an image of a wedding item and possibly a question or comment from the user.\n"
        "If the item is in the catalog, reply in the user's language, state that it is available, and always refer to the item by its exact Hebrew name as it appears in the catalog above (do not translate the item name).\n"
        "If the item is not in the catalog, reply in the user's language that it is not available and suggest similar wedding items from the catalog if possible, always using their Hebrew names as in the catalog.\n"
        "If the user asks in a language other than Hebrew, you must translate the rest of your response, but never translate the item names—always show them in Hebrew as in the catalog.\n"
    )

    try:
        image_bytes = file.read()
        # Compose the content list: system prompt, image, and user text if present
        content = [system_prompt]
        content.append({"mime_type": file.mimetype, "data": image_bytes})
        if user_text.strip():
            content.append("Respond in the language of the following text:")
            content.append(user_text.strip())
        else:
            content.append("Describe the wedding item in this image and check if it is in the catalog.")

        response = model.generate_content(content)
        gemini_reply = response.text
        gemini_reply = linkify_item_names(gemini_reply, item_names)
        
        logger.info(f"AI assistant image query processed", extra={'extra_data': {
            'language': lang,
            'has_user_text': bool(user_text.strip()),
            'user_text_length': len(user_text) if user_text else 0,
            'image_mimetype': file.mimetype,
            'response_length': len(gemini_reply)
        }})
        
        return jsonify({"reply": gemini_reply})
    except Exception as e:
        logger.error(f"Gemini API error in ask-image endpoint", exc_info=True, extra={'extra_data': {
            'language': lang,
            'has_user_text': bool(user_text.strip()),
            'image_mimetype': file.mimetype if file else None
        }})
        return jsonify({"error": "Gemini API error"}), 400
