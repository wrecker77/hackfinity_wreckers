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

    def draw_wrapped_text(self, x, y, w, h_limit, text, font_size, border=1):
        self.set_font("Arial", "", font_size)
        line_height = font_size + 1
        max_lines = int(h_limit / line_height)
        lines = []
        words = text.split()
        line = ""
        for word in words:
            if self.get_string_width(line + word + " ") > w:
                lines.append(line.strip())
                line = word + " "
                if len(lines) >= max_lines:
                    break
            else:
                line += word + " "
        if len(lines) < max_lines:
            lines.append(line.strip())
        for i, l in enumerate(lines[:max_lines]):
            self.set_xy(x, y + i * line_height)
            self.cell(w, line_height, l, border=border)
        return len(lines) * line_height

    def draw_product_cell(self, product, y_offset):
        cell_width = self.w * 0.9
        cell_height = self.h * 0.24
        x = (self.w - cell_width) / 2
        y = y_offset
        self.set_draw_color(160, 160, 160)
        self.rect(x, y, cell_width, cell_height)

        image_section_w = cell_width * 0.35
        text_section_w = cell_width * 0.6
        spacing = 3
        tx = x + image_section_w + spacing
        ty = y + 6
        label_w = text_section_w * 0.3
        value_w = text_section_w * 0.7 - spacing
        max_y = y + cell_height - 6

        # Image
        if product.get("image url"):
            try:
                img_w = image_section_w - 8
                img_h = cell_height - 12
                img_x = x + 4
                img_y = y + (cell_height - img_h) / 2
                self.image(product["image url"], x=img_x, y=img_y, w=img_w, h=img_h)
            except:
                pass

        # Product Fields
        self.set_font("Arial", "", 9)
        line_spacing = 3
        fields = [
            ("Product Name", product.get("product name", "")),
            ("Description", product.get("description", "")),
            ("Price", f"Rs. {product.get('price', 'N/A')}")
        ]

        for label, value in fields:
            if ty + 10 > max_y:
                break
            self.set_xy(tx, ty)
            self.set_font("Arial", "B", 9)
            self.cell(label_w, 5, label, border=1, align="L")
            value_x = tx + label_w + spacing
            value_y = ty
            self.set_font("Arial", "", 8)
            rendered_h = self.draw_wrapped_text(value_x, value_y, value_w, max_y - ty, value, 8, border=1)
            ty += max(rendered_h, 5) + line_spacing

        # Features
        features = product.get("features", [])
        if features and ty + 6 < max_y:
            self.set_xy(tx, ty)
            self.set_font("Arial", "B", 9)
            self.cell(label_w, 5, "Features", border=1, align="L")
            self.set_font("Arial", "", 7)
            cur_x = tx + label_w + spacing
            cur_y = ty
            line_height = 5
            space = 2

            for feature in features:
                fw = self.get_string_width(feature) + 6
                if cur_x + fw > tx + text_section_w:
                    cur_x = tx + label_w + spacing
                    cur_y += line_height + space
                if cur_y + line_height > max_y:
                    break
                self.set_fill_color(220, 240, 255)
                self.set_draw_color(100, 180, 255)
                self.set_xy(cur_x, cur_y)
                self.cell(fw, line_height, feature, border=1, align="C", fill=True)
                cur_x += fw + space

def generate_pdf_from_json(input_path, output_path="products.pdf"):
    with open(input_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)
    pdf = GradientBorderPDF()
    pdf.set_auto_page_break(auto=False)
    product_height = pdf.h * 0.24
    product_gap = 5
    top_margin = 10

    for category in json_data:
        if not isinstance(category, dict):
            continue

        products = category.get("products", [])
        cat_name = category.get("category name", "Unnamed Category")
        current_y = 0
        for product in products:
            if current_y == 0 or current_y + product_height > pdf.h - 10:
                pdf.add_page()
                current_y = pdf.draw_category_container(cat_name)

            pdf.draw_product_cell(product, current_y)
            current_y += product_height + product_gap

    pdf.output(output_path)
    print(f"✅ PDF generated: {output_path}")

