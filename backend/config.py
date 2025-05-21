import os

SECRET_KEY = 'your_very_secret_key'  # 请务必在生产环境中更改此密钥
UPLOAD_FOLDER = 'uploads'

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)