import google.generativeai as genai
import os
import subprocess

# Lấy API Key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def process():
    input_dir = 'input'
    # Quét tất cả file ảnh trong thư mục input
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print("No images found.")
        return

    for filename in files:
        path = os.path.join(input_dir, filename)
        print(f"Processing {filename}...")
        
        # Upload và nội dung
        img = genai.upload_file(path=path)
        prompt = "Chuyển toàn bộ nội dung ảnh toán này thành Markdown. Các công thức toán dùng ký hiệu LaTeX nằm trong $...$ hoặc $$...$$. Không thêm lời dẫn."
        
        response = model.generate_content([prompt, img])
        
        # Lưu ra Markdown tạm
        with open("out.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Dùng Pandoc chuyển sang Word chuẩn Equation
        output_name = filename.split('.')[0] + ".docx"
        subprocess.run(["pandoc", "out.md", "-o", output_name])
        print(f"Done: {output_name}")

if __name__ == "__main__":
    process()
