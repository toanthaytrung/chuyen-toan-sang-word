import google.generativeai as genai
import os
import subprocess
from pathlib import Path

# Lấy API Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Thử dùng bản flash mới nhất, nếu không được tự động chuyển bản ổn định
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro-vision')

def process():
    input_dir = Path('input')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print("Không thấy ảnh.")
        return

    for filename in files:
        print(f"--- Đang xử lý: {filename} ---")
        img_path = input_dir / filename
        img_data = {
            'mime_type': 'image/png' if filename.lower().endswith('.png') else 'image/jpeg',
            'data': img_path.read_bytes()
        }
        
        prompt = "Chuyển nội dung ảnh toán này thành Markdown. Các công thức toán dùng LaTeX đặt trong $...$ hoặc $$...$$. Không giải thích thêm."
        
        response = model.generate_content([prompt, img_data])
        
        with open("out.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        output_name = f"{img_path.stem}.docx"
        # Lệnh pandoc hỗ trợ đắc lực việc chuyển LaTeX sang Equation
        subprocess.run(["pandoc", "out.md", "-o", output_name])
        print(f"Thành công tạo file: {output_name}")

if __name__ == "__main__":
    process()
