from json_file_gen import make_file 
import streamlit as st
from pre_processing import process_user_input,categorize_products_with_cohere,refine_product_json

st.set_page_config(page_title="🛍️ Product Catalog Generator", layout="centered")

# 🎨 Custom Styling
st.markdown("""
    <style>
        .big-title {
            font-size: 2.5em;
            font-weight: 700;
            color: #1f77b4;
            text-align: center;
        }
        .product-box {
            background-color: #f9f9f9;
            padding: 1.5em;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            margin-bottom: 1.5em;
        }
        .product-name {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.5em;
        }
        .description-point {
            font-size: 0.95em;
            color: #555;
            margin-left: 1em;
        }
    </style>
""", unsafe_allow_html=True)

# 🏷️ App Header
st.markdown('<div class="big-title">🛍️ AI-Powered Product Catalog Generator</div>', unsafe_allow_html=True)
st.write("Add products one at a time. When you're ready, click **✨ Generate Catalog**.")

# Session state initialization
if "product_list" not in st.session_state:
    st.session_state.product_list = []
if "descriptions" not in st.session_state:
    st.session_state.descriptions = []
if "new_product" not in st.session_state:
    st.session_state.new_product = ""

# Input Field
new_product = st.text_input("➕ Enter a product", key="input_box", placeholder="e.g., Apple iPhone or Dove soap")

# Add Button
if st.button("➕ Add Product"):
    if new_product.strip():
        st.session_state.product_list.append(new_product.strip())
        st.session_state.new_product = ""  # Won't clear the box due to how Streamlit works

# Show product list so far
if st.session_state.product_list:
    st.markdown("#### ✅ Products Added:")
    st.write(", ".join(st.session_state.product_list))

# Generate Catalog Button
if st.button("✨ Generate Catalog"):
    if st.session_state.product_list:
        with st.spinner("🧠 Generating product descriptions..."):
            results = process_user_input(" ".join(st.session_state.product_list))
            products = ""
            filetered_list = {}
            for i in range(0,len(results)):
                products=products + str(i+1) + "." + results[i]["product name"] + ","
                filetered_list[results[i]["product name"]] = results[i]["description"]
            catogories = categorize_products_with_cohere(products)
            json_output = []
            for k in list(catogories):
                json_output.append({"category name": k ,"products":[refine_product_json({"product name":i,"description":filetered_list[i]}) for i in catogories[k]]})
            make_file(json_output)

    else:
        st.warning("Please add at least one product.")
exit(0)
# Display Catalog
if st.session_state.descriptions:
    st.markdown("---")
    st.markdown("### 📦 Product Catalog")
    for item in st.session_state.descriptions:
        bullet_lines = [line.strip() for line in item['description'].split('\n') if line.strip()]
        product_title = bullet_lines[0] if bullet_lines and bullet_lines[0].startswith("📦") else item['product_name']
        bullets_html = "".join(f"<li>{line.lstrip('*').strip()}</li>" for line in bullet_lines[1:])

        st.markdown(f"""
        <div class="product-box">
            <div class="product-name">{product_title}</div>
            <ul class="description-point">{bullets_html}</ul>
        </div>
        """, unsafe_allow_html=True)
