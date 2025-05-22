import os

SECRET_KEY = 'your_very_secret_key'  # 请务必在生产环境中更改此密钥
UPLOAD_FOLDER = 'uploads'

# 确保上传文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# SQLAlchemy 数据库配置
# 使用 PyMySQL 驱动: mysql+pymysql://username:password@host:port/database_name
# 如果使用 mysqlclient: mysql://username:password@host:port/database_name
DB_USERNAME = 'root'
DB_PASSWORD = 'ZY02287189' 
DB_HOST = 'localhost' 
DB_PORT = '3306'      # MySQL 默认端口
DB_NAME = 'face'

# SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
SQLALCHEMY_DATABASE_URI = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
SQLALCHEMY_TRACK_MODIFICATIONS = False # 禁用 Flask-SQLAlchemy 的事件系统，除非你需要它，可以提高性能
SQLALCHEMY_ECHO = False # 如果设置为 True，SQLAlchemy会打印执行的SQL语句，便于调试