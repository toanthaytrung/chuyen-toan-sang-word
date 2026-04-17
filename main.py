import google.generativeai as genai
import os
import subprocess
from pathlib import Path

# 1. Cấu hình
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 2. Tự động tìm model khả dụng (Tránh lỗi 404)
available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
# Ưu tiên flash, nếu không thì lấy cái đầu tiên trong danh sách
model_name = next((m for m in available_models if 'flash' in m), available_models[0])
print(f"Sử dụng model: {model_name}")
model = genai.GenerativeModel(model_name)

def process():
    input_dir = Path('input')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print("Không thấy ảnh.")
        return

    for filename in files:
        print(f"--- Đang xử lý: {filename} ---")
        img_path = input_dir / filename
        img_data = {'mime_type': 'image/png', 'data': img_path.read_bytes()}
        
        prompt = "Chuyển nội dung ảnh toán này thành Markdown. Các công thức toán dùng LaTeX đặt trong $...$ hoặc $$...$$. Không giải thích thêm."
        
        response = model.generate_content([prompt, img_data])
        
        # Ghi ra file tạm và chuyển sang Word
        with open("out.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        output_name = f"{img_path.stem}.docx"
        subprocess.run(["pandoc", "out.md", "-o", output_name])
        print(f"Thành công: {output_name}")

if __name__ == "__main__":
    process()
