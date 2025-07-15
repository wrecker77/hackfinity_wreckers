from fpdf import FPDF
import random
import colorsys
import sys
import json

class GradientBorderPDF(FPDF):
    def header(self):
        self.set_line_width(0.5)
        margin = 5
        steps = 100
        x1, y1 = margin, margin
        x2, y2 = self.w - margin, self.h - margin
        self.draw_gradient_line(x1, y1, x2, y1, steps)
        self.draw_gradient_line(x2, y1, x2, y2, steps)
        self.draw_gradient_line(x2, y2, x1, y2, steps)
        self.draw_gradient_line(x1, y2, x1, y1, steps)

    def draw_gradient_line(self, x_start, y_start, x_end, y_end, steps):
        r1, g1, b1 = self.filtered_vivid_color()
        r2, g2, b2 = self.filtered_vivid_color()
        dx = (x_end - x_start) / steps
        dy = (y_end - y_start) / steps
        for i in range(steps):
            r = int(r1 + (r2 - r1) * i / steps)
            g = int(g1 + (g2 - g1) * i / steps)
            b = int(b1 + (b2 - b1) * i / steps)
            self.set_draw_color(r, g, b)
            self.line(x_start + dx * i, y_start + dy * i,
                      x_start + dx * (i + 1), y_start + dy * (i + 1))

    def filtered_vivid_color(self):
        for _ in range(10):
            h = random.random()
            if 0.05 < h < 0.1 or 0.25 < h < 0.4:
                continue
            s = 0.75 + random.uniform(0.1, 0.2)
            v = 0.75 + random.uniform(0.05, 0.15)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            return int(r * 255), int(g * 255), int(b * 255)
        return 100, 140, 255

    def draw_category_container(self, name):
        cat_height = self.h * 0.1
        self.set_xy(0, 10)
        self.set_font("Arial", "B", 14)
        self.set_fill_color(230, 230, 250)
        self.set_text_color(0, 0, 0)
        self.rect(10, 10, self.w - 20, cat_height, 'DF')
        self.set_xy(10, 10 + (cat_height - 10) / 2)
        self.cell(self.w - 20, 10, name, align="C")
        return 10 + cat_height + 5

    def draw_product_cell(self, product, y_offset):
        cell_width = self.w * 0.9
        cell_height = self.h * 0.24
        x = (self.w - cell_width) / 2
        y = y_offset
        self.set_draw_color(160, 160, 160)
        self.rect(x, y, cell_width, cell_height)

        image_section_w = cell_width * 0.4
        text_section_w = cell_width * 0.6
        spacing = 3

        if product.get("image url"):
            try:
                img_w = image_section_w - 10
                img_h = cell_height - 10
                img_x = x + 5
                img_y = y + (cell_height - img_h) / 2
                self.image(product["image url"], x=img_x, y=img_y, w=img_w, h=img_h)
            except:
                pass

        tx = x + image_section_w + 5
        ty = y + 6
        label_w = text_section_w * 0.3
        value_w = text_section_w * 0.7 - spacing

        fields = [
            ("Product Name", product.get("product name", "")),
            ("Description", product.get("description", "")),
            ("Price", f"Rs. {product.get('price', 'N/A')}")
        ]

        for label, value in fields:
            if ty + 6 > y + cell_height - 8:
                break
            self.set_xy(tx, ty)
            self.set_font("Arial", "B", 9)
            self.set_fill_color(245, 245, 245)
            self.set_draw_color(180, 180, 180)
            self.cell(label_w, 6, label, border=1, align="C", fill=True)
            self.set_font("Arial", "", 9)
            self.set_x(tx + label_w + spacing)
            self.cell(value_w, 6, value, border=1, ln=1, align="C", fill=False)
            ty += 8

        features = product.get("features", [])
        if features and ty + 6 < y + cell_height - 8:
            self.set_xy(tx, ty)
            self.set_font("Arial", "B", 9)
            self.set_fill_color(245, 245, 245)
            self.cell(label_w, 6, "Features", border=1, align="C", fill=True)

            max_width = text_section_w * 0.7 - spacing
            cur_x = tx + label_w + spacing
            cur_y = ty
            space = 2
            line_height = 6
            self.set_font("Arial", "", 8)

            for feature in features:
                fw = self.get_string_width(feature) + 6
                if cur_x + fw > tx + text_section_w:
                    cur_x = tx + label_w + spacing
                    cur_y += line_height + space
                if cur_y + line_height > y + cell_height - 6:
                    break
                self.set_xy(cur_x, cur_y)
                self.set_fill_color(200, 240, 255)
                self.set_draw_color(150, 200, 230)
                self.cell(fw, line_height, feature, border=1, ln=0, align="C", fill=True)
                cur_x += fw + space

def generate_pdf_from_json(json_data, output_path="products.pdf"):
    pdf = GradientBorderPDF()
    pdf.set_auto_page_break(auto=True, margin=10)

    for category in json_data:
        if not isinstance(category, dict):
            continue  # Skip if category is malformed

        products = category.get("products", [])
        cat_name = category.get("category name", "Unnamed Category")
        category_written = False
        first_product_y = 0

        product_height = pdf.h * 0.24
        product_gap = 5

        for i, product in enumerate(products):
            if i % 3 == 0:
                pdf.add_page()
                if not category_written:
                    first_product_y = pdf.draw_category_container(cat_name)
                    category_written = True

            y_offset = first_product_y + (i % 3) * (product_height + product_gap)
            pdf.draw_product_cell(product, y_offset)

    pdf.output(output_path)
    print(f"✅ PDF generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <input.json>")
        sys.exit(1)

    input_path = sys.argv[1]

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")
        sys.exit(1)

    generate_pdf_from_json(data)
