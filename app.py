import streamlit as st
import json
import os
from PIL import Image

def render():


    st.set_page_config(page_title="🛍️ Catalog Viewer & Editor", layout="wide")
    st.title("📋 Product Catalog")

    CATALOG_PATH = "catalog.json"
    IMAGE_DIR = "uploaded_images"

    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    # Load catalog JSON data
    def load_catalog():
        if not os.path.exists(CATALOG_PATH):
            return []
        with open(CATALOG_PATH, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    # Load and store in session_state on first run
    if "rows" not in st.session_state:
        catalog = load_catalog()
        rows = []
        for category in catalog:
            for product in category.get("products", []):
                rows.append(product)
        st.session_state.rows = rows

    # CSS styling
    st.markdown("""
        <style>
        .header-row, .data-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #ddd;
            padding: 0.5rem;
            font-size: 15px;
        }
        .header-row {
            font-weight: bold;
            background-color: #4f8bf9;
            color: white;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        }
        .col {
            flex: 1;
            text-align: center;
        }
        .col-img {
            flex: 1;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class='header-row'>
        <div class='col'>S.No</div>
        <div class='col-img'>Image</div>
        <div class='col'>Product Name</div>
        <div class='col'>Description</div>
        <div class='col'>Features</div>
        <div class='col'>Price</div>
        <div class='col'>Edit</div>
    </div>
    """, unsafe_allow_html=True)

    # Data rows
    for i, item in enumerate(st.session_state.rows):
        is_editing = st.session_state.get(f"editing_{i}", False)
        row_key = f"row_{i}"

        # Initialize editable values
        if f"{row_key}_name" not in st.session_state:
            st.session_state[f"{row_key}_name"] = item["product name"]
            st.session_state[f"{row_key}_desc"] = item["description"]
            st.session_state[f"{row_key}_features"] = ", ".join(item["features"])
            st.session_state[f"{row_key}_price"] = item["price"]

        cols = st.columns([0.5, 1.2, 1.5, 2, 1.5, 1, 0.5])

        # 1. S.No
        cols[0].markdown(f"**{i+1}**", unsafe_allow_html=True)

        # 2. Image
        current_img = item.get("image url", "")
        if os.path.exists(current_img):
            cols[1].image(current_img, width=60)
        else:
            cols[1].markdown("*No image*", unsafe_allow_html=True)

        if is_editing:
            img_file = cols[1].file_uploader("", type=["png", "jpg", "jpeg"], label_visibility="collapsed", key=f"img_{i}")
            if img_file:
                img_path = os.path.join(IMAGE_DIR, f"product_{i}.png")
                with open(img_path, "wb") as f:
                    f.write(img_file.read())
                item["image url"] = img_path

        # 3. Product Name
        if is_editing:
            st.session_state[f"{row_key}_name"] = cols[2].text_input("", value=st.session_state[f"{row_key}_name"], label_visibility="collapsed", key=f"name_{i}")
        else:
            cols[2].markdown(item["product name"], unsafe_allow_html=True)

        # 4. Description
        if is_editing:
            st.session_state[f"{row_key}_desc"] = cols[3].text_input("", value=st.session_state[f"{row_key}_desc"], label_visibility="collapsed", key=f"desc_{i}")
        else:
            cols[3].markdown(item["description"], unsafe_allow_html=True)

        # 5. Features
        if is_editing:
            st.session_state[f"{row_key}_features"] = cols[4].text_input("", value=st.session_state[f"{row_key}_features"], label_visibility="collapsed", key=f"feat_{i}")
        else:
            cols[4].markdown(", ".join(item["features"]), unsafe_allow_html=True)

        # 6. Price
        if is_editing:
            st.session_state[f"{row_key}_price"] = cols[5].text_input("", value=st.session_state[f"{row_key}_price"], label_visibility="collapsed", key=f"price_{i}")
        else:
            cols[5].markdown(item["price"], unsafe_allow_html=True)

        # 7. Edit button
        if cols[6].button("✏️", key=f"edit_btn_{i}"):
            st.session_state[f"editing_{i}"] = not is_editing

    # Save Button
    if st.button("💾 Save Changes"):
        try:
            for i, item in enumerate(st.session_state.rows):
                row_key = f"row_{i}"
                item["product name"] = st.session_state[f"{row_key}_name"]
                item["description"] = st.session_state[f"{row_key}_desc"]
                item["features"] = [f.strip() for f in st.session_state[f"{row_key}_features"].split(",") if f.strip()]
                item["price"] = st.session_state[f"{row_key}_price"]

            updated_catalog = [{"products": st.session_state.rows}]
            with open(CATALOG_PATH, "w") as f:
                json.dump(updated_catalog, f, indent=2)
            st.success("✅ Catalog updated and saved successfully!")
        except Exception as e:
            st.error(f"❌ Failed to save catalog: {e}")
