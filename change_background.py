import cv2
import numpy as np
from rembg import remove

def change_background(image_path, output_path, new_background_color):
    """
    ฟังก์ชันสำหรับเปลี่ยนพื้นหลังของรูปภาพโดยใช้ไลบรารี rembg เพื่อลบพื้นหลังเดิมออก
    
    Parameters:
    image_path (str): เส้นทางของไฟล์รูปภาพต้นฉบับ
    output_path (str): เส้นทางสำหรับบันทึกไฟล์รูปภาพใหม่ที่เปลี่ยนพื้นหลังแล้ว
    new_background_color (list): ค่าสีพื้นหลังใหม่ในรูปแบบ BGR (เช่น [128, 0, 0] สำหรับสีน้ำเงิน)
    """
    try:
        # อ่านไฟล์รูปภาพต้นฉบับ
        image = cv2.imread(image_path)
        if image is None:
            print(f"ข้อผิดพลาด: ไม่พบไฟล์รูปภาพที่ '{image_path}'")
            return

        # ลบพื้นหลังด้วยไลบรารี rembg ซึ่งจะสร้างไฟล์ที่มี Alpha Channel
        output_image_rgba = remove(image)
        
        # แยก Channel B, G, R, และ Alpha ออกจากกัน
        b, g, r, alpha = cv2.split(output_image_rgba)
        
        # รวม Channel BGR กลับมาเป็นภาพ Foreground (ภาพคน)
        foreground = cv2.merge((b, g, r))
        
        # สร้างภาพพื้นหลังใหม่ที่มีสีตามที่กำหนด
        new_background = np.full(image.shape, new_background_color, dtype=np.uint8)
        
        # แปลงค่า Alpha Channel ให้เป็น float เพื่อใช้ในการคำนวณ
        alpha_float = alpha.astype(float) / 255.0
        alpha_3channel = cv2.merge([alpha_float, alpha_float, alpha_float])

        # ผสานภาพ Foreground เข้ากับพื้นหลังใหม่
        final_image = (foreground * alpha_3channel) + (new_background * (1 - alpha_3channel))
        final_image = final_image.astype(np.uint8)
        
        # บันทึกไฟล์รูปภาพที่ได้
        cv2.imwrite(output_path, final_image)
        print(f"บันทึกไฟล์สำเร็จ: {output_path}")

    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

def main_program():
    """
    ฟังก์ชันหลักสำหรับเริ่มต้นโปรแกรม
    """
    print("--- โปรแกรมเปลี่ยนพื้นหลังภาพ ---")
    
    # กำหนดค่าเริ่มต้น
    input_file = "photo.jpg"
    output_file = "photo_blue_bg.jpg"
    blue_background = [128, 0, 0]  # BGR format for blue

    # เรียกใช้ฟังก์ชันเปลี่ยนพื้นหลัง
    change_background(input_file, output_file, blue_background)

if __name__ == "__main__":
    main_program()