import google.generativeai as genai
import os
import subprocess
import time
from pathlib import Path

# Cấu hình API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    input_dir = Path('input')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))]
    
    if not files:
        print("Trống trơn thầy ơi!")
        return

    # Xóa file Word cũ
    for old_docx in Path('.').glob("*.docx"):
        old_docx.unlink()

    for filename in files:
        print(f"--- Đang xử lý: {filename} ---")
        file_path = input_dir / filename
        
        # 1. Tải file lên
        raw_file = genai.upload_file(path=str(file_path))
        
        # 2. Đợi cho đến khi Google xử lý xong file (CỰC KỲ QUAN TRỌNG CHO PDF)
        while raw_file.state.name == "PROCESSING":
            print("Đợi xíu, Gemini đang đọc file...")
            time.sleep(5)
            raw_file = genai.get_file(raw_file.name)

        # 3. Ra lệnh biên soạn
        prompt = "Chuyển nội dung file này thành Markdown. Các công thức toán dùng LaTeX trong $...$ hoặc $$...$$. Trình bày chuẩn đề thi trắc nghiệm Bộ GD."
        
        response = model.generate_content([prompt, raw_file])
        
        with open("out.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        output_name = f"{file_path.stem}.docx"
        subprocess.run(["pandoc", "out.md", "-o", output_name])
        print(f"==> Xong: {output_name}")

if __name__ == "__main__":
    process()
