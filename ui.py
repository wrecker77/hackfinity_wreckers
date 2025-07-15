import streamlit as st
from pre_processing import process_user_input

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
st.write("Enter your product list below. You can type in natural language (e.g., 'Nike shoes and Dove shampoo').")

# 📥 Text Input
user_input = st.text_area("Product Input", placeholder="Type or paste your product list here...", height=100)

# 🎙️ Voice Button Placeholder
st.button("🎤 Use Voice Input (Coming Soon!)")

# 🧠 Generate Button
if st.button("✨ Generate Catalog"):
    if user_input.strip():
        with st.spinner("Processing your products..."):
            results = process_user_input(user_input)

        st.markdown("---")
        for item in results:
            st.markdown(f"""
            <div class="product-box">
                <div class="product-name">📦 {item['product_name']}</div>
                <div class="description-point">{item['description'].replace('-', '<br>-')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Please enter a product list first.")
