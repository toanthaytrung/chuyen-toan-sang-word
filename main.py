import google.generativeai as genai
import os
import subprocess
from pathlib import Path

# Cấu hình API
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Tự động tìm model
available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
model_name = next((m for m in available_models if 'flash' in m), available_models[0])
model = genai.GenerativeModel(model_name)

def process():
    input_dir = Path('input')
    files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print("Không thấy ảnh trong thư mục input.")
        return

    for filename in files:
        print(f"--- Đang xử lý: {filename} ---")
        img_path = input_dir / filename
        img_data = {'mime_type': 'image/png', 'data': img_path.read_bytes()}
        
        # CÂU LỆNH CHUẨN ĐỀ THI BỘ GD&ĐT
        prompt = """
        Bạn là chuyên gia biên soạn đề thi Toán. Hãy chuyển ảnh này thành Markdown theo định dạng chuẩn của Bộ Giáo dục Việt Nam:
        1. CÔNG THỨC: Tất cả ký hiệu và công thức toán phải nằm trong $...$ hoặc $$...$$.
        2. PHÂN LOẠI CÂU HỎI:
           - Trắc nghiệm 4 lựa chọn: Ghi 'Câu X.', các phương án A, B, C, D in đậm. Nếu ngắn thì để trên 1 dòng, dài thì xuống dòng.
           - Trắc nghiệm Đúng/Sai: Trình bày thành bảng hoặc danh sách. Mỗi ý a), b), c), d) phải rõ ràng.
           - Câu trả lời ngắn: Ghi 'Câu X.' và để khoảng trống hoặc ghi 'Đáp số:....'
        3. TRÌNH BÀY: 
           - In đậm chữ 'Câu X:', 'A.', 'B.', 'C.', 'D.', 'a)', 'b)', 'c)', 'd)'.
           - Đảm bảo cấu trúc rõ ràng, không thêm lời dẫn giải của AI.
        """
        
        response = model.generate_content([prompt, img_data])
        
        # Lưu Markdown
        with open("out.md", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Chuyển sang Word (docx)
        output_name = f"{img_path.stem}.docx"
        # Thêm tham số --reference-doc nếu thầy có file mẫu (tạm thời để mặc định)
        subprocess.run(["pandoc", "out.md", "-o", output_name])
        print(f"Thành công: {output_name}")

if __name__ == "__main__":
    process()
