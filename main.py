import google.generativeai as genai
import os
import subprocess
from pathlib import Path

# Cấu hình API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    input_dir = Path('input')
    # Quét ảnh
    extensions = ('.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(extensions)]
    
    if not files:
        print("Không tìm thấy ảnh trong thư mục input.")
        return

    for filename in files:
        print(f"Đang xử lý: {filename}...")
        img_path = input_dir / filename
        
        # Đọc dữ liệu ảnh trực tiếp
        img_data = {
            'mime_type': 'image/png' if filename.lower().endswith('.png') else 'image/jpeg',
            'data': img_path.read_bytes()
        }
        
        prompt = "Chuyển nội dung ảnh toán này thành Markdown. Các công thức toán dùng LaTeX trong $...$ hoặc $$...$$. Không thêm lời dẫn."
        
        # Gọi Gemini
        response = model.generate_content([prompt, img_data])
        
        # Tạo file Markdown tạm
        with open("out.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Xuất ra Word bằng Pandoc
        output_name = f"{img_path.stem}.docx"
        subprocess.run(["pandoc", "out.md", "-o", output_name])
        print(f"Đã tạo file: {output_name}")

if __name__ == "__main__":
    process()
