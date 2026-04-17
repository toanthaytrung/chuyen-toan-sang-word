import google.generativeai as genai
import os
import subprocess
import time
from pathlib import Path

# 1. Cấu hình
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    input_dir = Path('input')
    # Quét cả ảnh và PDF
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))]
    
    if not files:
        print("Không có file nào trong thư mục input.")
        return

    # Xóa file kết quả cũ
    for old_file in Path('.').glob("*.docx"):
        old_file.unlink()

    for filename in files:
        print(f"--- Đang xử lý: {filename} ---")
        file_path = input_dir / filename
        
        # Tải file lên Gemini
        raw_file = genai.upload_file(path=str(file_path))
        
        # Đợi file xử lý xong (quan trọng cho PDF)
        while raw_file.state.name == "PROCESSING":
            time.sleep(5)
            raw_file = genai.get_file(raw_file.name)

        # Ra lệnh chuyển đổi chuẩn Bộ GD
        prompt = """
        Bạn là chuyên gia số hóa đề thi. Hãy chuyển file này thành Markdown:
        1. Công thức dùng LaTeX trong $...$ hoặc $$...$$.
        2. Trình bày chuẩn 3 dạng: Trắc nghiệm 4 lựa chọn, Đúng/Sai, Trả lời ngắn.
        3. In đậm Câu, đáp án A. B. C. D. và các ý a) b) c) d).
        """
        
        response = model.generate_content([prompt, raw_file])
        
        # Ghi ra Markdown và chuyển sang Word
        with open("out.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        output_name = f"{file_path.stem}.docx"
        subprocess.run(["pandoc", "out.md", "-o", output_name])
        
        # TỰ ĐỘNG XÓA FILE INPUT SAU KHI XỬ LÝ (Để lần sau thư mục luôn sạch)
        file_path.unlink()
        print(f"==> Hoàn thành: {output_name} và đã dọn dẹp file nguồn.")

if __name__ == "__main__":
    process()
