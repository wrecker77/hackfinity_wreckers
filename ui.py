import streamlit as st
from pre_processing import process_user_input

# Set up app UI config
st.set_page_config(page_title="🛍️ Product Catalog Generator", layout="centered")

# --- Inject Custom Styling ---
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
        .product-list {
            margin-top: 1em;
            font-size: 1em;
            color: #444;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="big-title">🛍️ AI-Powered Product Catalog Generator</div>', unsafe_allow_html=True)
st.write("Type your product descriptions one at a time. Once done, click **Generate Catalog**.")

# --- Session State Setup ---
if 'product_inputs' not in st.session_state:
    st.session_state.product_inputs = []

# --- Product Input ---
new_product = st.text_input("Enter a product or messy product sentence:", key="input_product")

# --- Add Button ---
if st.button("➕ Add Product"):
    if new_product.strip():
        st.session_state.product_inputs.append(new_product.strip())
        st.success(f"✅ Added: `{new_product.strip()}`")
        # Optionally clear the input field (can't directly reset st.text_input)
        st.rerun()
    else:
        st.warning("Please enter a valid product input before adding.")

# --- Show Current Product List ---
if st.session_state.product_inputs:
    st.markdown("#### 🧾 Products Added:")
    st.markdown("<ul class='product-list'>" + "".join(f"<li>{p}</li>" for p in st.session_state.product_inputs) + "</ul>", unsafe_allow_html=True)

# --- Generate Catalog ---
if st.button("✨ Generate Catalog"):
    if st.session_state.product_inputs:
        with st.spinner("Generating your product catalog..."):
            combined_input = ". ".join(st.session_state.product_inputs)
            results = process_user_input(combined_input)

        st.markdown("---")
        st.markdown("### 📘 Generated Product Catalog:")
        for item in results:
            st.markdown(f"""
            <div class="product-box">
                <div class="product-name">📦 {item['product_name']}</div>
                <div class="description-point">{item['description'].replace('-', '<br>-')}</div>
            </div>
            """, unsafe_allow_html=True)

        # Reset for next use
        st.session_state.product_inputs = []
    else:
        st.warning("Please add at least one product before generating the catalog.")
