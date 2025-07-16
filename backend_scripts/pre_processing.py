import cohere
import re
from langdetect import detect
from deep_translator import GoogleTranslator

# Initialize Cohere
co = cohere.ClientV2("Fz8g3YpIHL4sN7bW0zAXXi03oS8Ek1RQYvSUZdaP")  # Use your actual API key


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


# 2. Ask Cohere to extract clean list of product names
def extract_product_list(raw_text: str):
    prompt = f"""
You will be given a user-written messy product input text. Extract a clean list of **distinct product names** from it. 
Each product should be written clearly without brand repetitions or joining multiple products into one.

Input:
\"\"\"
{raw_text}
\"\"\"

Output format (return ONLY the list):
- Product 1
- Product 2
- Product 3
    """.strip()

    res = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt}]
    )

    # Extract product list from AI response
    text = "\n".join([msg.text for msg in res.message.content if msg.type == "text"])
    products = re.findall(r"- (.+)", text)
    return [p.strip() for p in products if p.strip()]


# 3. Prompt generation for a single product
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


# 4. Extract text response from Cohere
def extract_description_from_response(res):
    return "\n".join([
        item.text for item in res.message.content 
        if item.type == "text"
    ])


# 5. Generate detailed description for one product
def generate_description(product_text: str):
    prompt = generate_prompt(product_text)
    res = co.chat(
        model="command-a-03-2025",
        messages=[{"role": "user", "content": prompt}]
    )
    return extract_description_from_response(res)


# 6. Main pipeline: translate → extract product list → generate descriptions
def process_user_input(raw_input: str):
    translated = translate_to_english(raw_input)
    product_list = extract_product_list(translated)

    results = []
    for product in product_list:
        description = generate_description(product)
        product_match = re.search(r"📦\s*(.+)", description)
        product_name = product_match.group(1).strip() if product_match else product[:20]
        results.append({
            "product_name": product_name,
            "description": description
        })

    return results
