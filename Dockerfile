# ใช้ Python เวอร์ชัน 3.10 เป็น Base Image
FROM python:3.10-slim

# ติดตั้งแพ็กเกจของระบบปฏิบัติการที่จำเป็นสำหรับ OpenCV และไลบรารีอื่นๆ
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# กำหนด Working Directory
WORKDIR /app

# คัดลอกไฟล์ requirements.txt
COPY requirements.txt .

# ติดตั้งไลบรารี Python จากไฟล์ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดส่วนที่เหลือของโปรเจกต์
COPY . .

# กำหนด Port ที่ Gunicorn จะใช้งาน
EXPOSE 8000

# คำสั่งหลักในการรันแอปพลิเคชันด้วย Gunicorn
# Gunicorn จะใช้ไฟล์ app.py และรัน Flask App ที่ชื่อว่า app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]