import os
import cv2
import numpy as np
from rembg import remove
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

# สร้างโฟลเดอร์สำหรับอัปโหลดและผลลัพธ์
UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.secret_key = os.urandom(24)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def change_background(image_path, output_path, new_background_color_hex):
    """
    ฟังก์ชันสำหรับเปลี่ยนพื้นหลังของรูปภาพ
    
    Parameters:
    image_path (str): เส้นทางของไฟล์รูปภาพต้นฉบับ
    output_path (str): เส้นทางสำหรับบันทึกไฟล์รูปภาพใหม่ที่เปลี่ยนพื้นหลังแล้ว
    new_background_color_hex (str): ค่าสีพื้นหลังใหม่ในรูปแบบ Hex code (เช่น '#0000FF')
    """
    try:
        # แปลง Hex code เป็นค่าสี BGR
        new_background_color_hex = new_background_color_hex.lstrip('#')
        new_background_color = tuple(int(new_background_color_hex[i:i+2], 16) for i in (4, 2, 0))

        image = cv2.imread(image_path)
        if image is None:
            return False, "ไม่พบไฟล์รูปภาพ"

        output_image_rgba = remove(image)
        b, g, r, alpha = cv2.split(output_image_rgba)
        foreground = cv2.merge((b, g, r))
        
        new_background = np.full(image.shape, new_background_color, dtype=np.uint8)
        
        alpha_float = alpha.astype(float) / 255.0
        alpha_3channel = cv2.merge([alpha_float, alpha_float, alpha_float])

        final_image = (foreground * alpha_3channel) + (new_background * (1 - alpha_3channel))
        final_image = final_image.astype(np.uint8)
        
        cv2.imwrite(output_path, final_image)
        return True, "สำเร็จ"
    except Exception as e:
        return False, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ตรวจสอบว่ามีการอัปโหลดไฟล์หรือไม่
        if 'file' not in request.files:
            return render_template('index.html', error='ไม่พบไฟล์')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='กรุณาเลือกไฟล์')
        if not allowed_file(file.filename):
            return render_template('index.html', error='อนุญาตเฉพาะไฟล์นามสกุล .png, .jpg, .jpeg เท่านั้น')

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # รับค่าสีจากฟอร์ม
            selected_color = request.form.get('color_picker')
            
            output_filename = f"result_{os.path.splitext(filename)[0]}.png"
            output_filepath = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

            # เรียกใช้ฟังก์ชันเปลี่ยนพื้นหลัง
            success, message = change_background(filepath, output_filepath, selected_color)

            if success:
                return render_template('index.html', result_image=output_filename)
            else:
                return render_template('index.html', error=message)

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
