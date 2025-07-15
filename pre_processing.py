import cohere
import re
from langdetect import detect
from deep_translator import GoogleTranslator

# Initialize Cohere
co = cohere.ClientV2("Fz8g3YpIHL4sN7bW0zAXXi03oS8Ek1RQYvSUZdaP")  # Replace with your actual API key


# 1. Detect language and translate to English (if needed)
def translate_to_english(text: str) -> str:
    try:
        lang = detect(text)
        if lang != 'en':
            translated = GoogleTranslator(source='auto', target='en').translate(text)
            return translated
        return text
    except Exception:
        return text


# 2. Split input text into multiple product segments (heuristic approach)
def split_products(text: str):
    # Break by possible indicators of different items
    product_lines = re.split(r"[.\n]|(?:\band\b)|(?:\bwith\b)|(?:\balso\b)|(?:,)|(?:\+)|(?:\/)", text)
    cleaned = [p.strip() for p in product_lines if p.strip()]
    return cleaned


# 3. Prompt generation for individual product
def generate_prompt(product_details: str) -> str:
    return f"""
You are creating a professional product catalog.

For the following product, generate exactly **5 separate bullet points**.
Each point should be under 25 words and highlight a key feature, use, or benefit.
Avoid combining multiple products into one description.
Do not merge unrelated product details.

PRODUCT DETAILS:
\"\"\"
{product_details}
\"\"\"

Return output in this format:

📦 <Product Name>
* Point 1
* Point 2
* Point 3
* Point 4
* Point 5
""".strip()


# 4. Extract only text responses
def extract_description_from_response(res):
    return "\n".join([
        item.text for item in res.message.content 
        if item.type == "text"
    ])


# 5. Generate description via Cohere
def generate_description(product_text: str):
    prompt = generate_prompt(product_text)

    res = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt}]
    )

    return extract_description_from_response(res)


# 6. Master function: process full user input
def process_user_input(raw_input: str):
    translated = translate_to_english(raw_input)
    product_chunks = split_products(translated)

    results = []
    for chunk in product_chunks:
        description = generate_description(chunk)
        
        # Extract the product name from the first 📦 line
        product_match = re.search(r"📦\s*(.+)", description)
        product_name = product_match.group(1).strip() if product_match else chunk[:20]

        results.append({
            "product_name": product_name,
            "description": description
        })

    return results


# 7. Example usage
if __name__ == "__main__":
    user_input = "dove shampoo kercheif addidas shoe rolex watch"
    output = process_user_input(user_input)

    for item in output:
        print(f"\n📦 {item['product_name']}\n{item['description']}")
