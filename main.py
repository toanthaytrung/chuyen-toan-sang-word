import google.generativeai as genai
import os
import subprocess
import sys

# 1. Lấy API Key từ hệ thống bảo mật của GitHub
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def process_math_document():
    # Tìm file ảnh trong thư mục 'input'
    input_dir = 'input'
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        print("Hãy cho ảnh vào thư mục 'input' rồi chạy lại nhé.")
        return

    files = os.listdir(input_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))]

    if not image_files:
        print("Không tìm thấy file ảnh nào trong thư mục 'input'.")
        return

    for filename in image_files:
        path = os.path.join(input_dir, filename)
        print(f"Đang xử lý file: {filename}...")

        # Tải ảnh lên Gemini
        sample_file = genai.upload_file(path=path)
        
        # Yêu cầu Gemini gõ lại nội dung
        prompt = """
        Hãy chuyển nội dung trong ảnh này thành văn bản Markdown. 
        Yêu cầu:
        1. Các công thức toán học PHẢI được để trong cặp dấu $$...$$ (đối với công thức dòng riêng) hoặc $...$ (đối với công thức trong dòng).
        2. Không thêm bất kỳ lời giải thích nào khác ngoài nội dung trong ảnh.
        3. Đảm bảo các ký hiệu toán học chính xác theo chuẩn LaTeX.
        """
        
        response = model.generate_content([prompt, sample_file])
        markdown_content = response.text
        
        # Lưu ra file tạm
        with open("temp.md", "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        # 2. Sử dụng Pandoc để chuyển sang Word (.docx)
        output_filename = os.path.splitext(filename)[0] + ".docx"
        try:
            # Lệnh chạy Pandoc để biến mã LaTeX thành Word Equation
            subprocess.run([
                "pandoc", "temp.md", 
                "-o", output_filename,
                "--from", "markdown",
                "--to", "docx"
            ], check=True)
            print(f"Đã xuất file Word: {output_filename}")
        except Exception as e:
            print(f"Lỗi khi xuất Word: {e}")

if __name__ == "__main__":
    process_math_document()
