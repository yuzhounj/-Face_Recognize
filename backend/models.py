from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid # 用于生成默认的 UUID

# 创建 SQLAlchemy 对象，但不在此时绑定到 app
# 我们将在 app.py 中初始化它并传递 app 实例
db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    face_data = db.Column(db.Text, nullable=False)  # 存储模拟的特征向量，用Text可以存较长字符串
    photo_filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 定义与签到记录的一对多关系
    # backref='user' 使得可以在 AttendanceRecord 对象上通过 .user 访问关联的 User 对象
    # lazy=True (默认) 表示 SQLAlchemy 会在第一次访问时按需加载相关对象
    attendance_records = db.relationship('AttendanceRecord', backref='user', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.name} ({self.id})>'

class AttendanceRecord(db.Model):
    __tablename__ = 'attendance_records'

    id = db.Column(db.Integer, primary_key=True) # 自动递增的 ID
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    # name 字段可以冗余存储，也可以通过 user_id 关联查询User表得到。此处选择不冗余，通过关联查询。
    # name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<AttendanceRecord for user_id={self.user_id} at {self.timestamp}>' 