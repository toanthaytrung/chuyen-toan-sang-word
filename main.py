import google.generativeai as genai
import os
import subprocess
from pathlib import Path

# Cấu hình API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Tự động tìm model (Ưu tiên bản 1.5 Flash vì nó xử lý tài liệu dài rất tốt)
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    input_dir = Path('input')
    # Quét tất cả file trong input (ảnh và pdf)
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))]
    
    if not files:
        print("Trống trơn, không có gì để làm thầy ơi!")
        return

    # Xóa các file Word cũ (.docx) đang nằm ở thư mục ngoài để không bị lẫn
    for old_docx in Path('.').glob("*.docx"):
        old_docx.unlink()

    for filename in files:
        print(f"--- Đang xử lý file mới: {filename} ---")
        file_path = input_dir / filename
        
        # Tải file lên Gemini (Gemini hỗ trợ đọc PDF trực tiếp cực mạnh)
        uploaded_file = genai.upload_file(path=str(file_path))
        
        prompt = """
        Bạn là chuyên gia số hóa đề thi Toán chuyên nghiệp. 
        Hãy đọc toàn bộ các trang trong file này và chuyển thành văn bản Markdown:
        1. Giữ nguyên thứ tự câu hỏi từ đầu đến cuối.
        2. CÔNG THỨC: Tất cả dùng LaTeX trong $...$ hoặc $$...$$.
        3. PHÂN LOẠI: 
           - Câu trắc nghiệm 4 lựa chọn (A, B, C, D).
           - Câu trắc nghiệm Đúng/Sai (a, b, c, d).
           - Câu trả lời ngắn.
        4. TRÌNH BÀY: In đậm 'Câu X:', 'A.', 'B.', 'a)', 'b)'... trình bày chuẩn đề thi của Bộ.
        """
        
        # Chờ file upload xử lý xong rồi mới gọi Content
        response = model.generate_content([prompt, uploaded_file])
        
        # Lưu Markdown tạm
        with open("out.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Chuyển sang Word bằng Pandoc
        output_name = f"{file_path.stem}.docx"
        subprocess.run(["pandoc", "out.md", "-o", output_name])
        print(f"==> Đã xong file Word cho: {filename}")

if __name__ == "__main__":
    process()
