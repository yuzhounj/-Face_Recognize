import os
import uuid
from datetime import datetime
from models import db, User, AttendanceRecord # From models.py
from sqlalchemy.exc import SQLAlchemyError

# --- Private Helper Function for Mock Data Extraction ---
def _extract_mock_face_data(image_file):
    """(Internal) 模拟从图片对象中提取人脸特征数据。"""
    # image_file.filename 可能会因为文件名包含特殊字符而出错，实际库会更健壮
    # 为了演示，我们假设 filename 是安全的
    safe_filename_part = os.path.basename(str(image_file.filename)) # 获取文件名部分，尝试转为str
    mock_face_data = f"mock_feature_vector_{uuid.uuid4().hex[:10]}_for_{safe_filename_part}"
    print(f"模拟人脸数据提取：为图片 '{safe_filename_part}' 生成特征数据: {mock_face_data}")
    return mock_face_data

# --- Public Functions ---

# 用于注册：保存照片，并提取特征数据
def save_photo_and_extract_data(image_file, upload_folder):
    """
    保存上传的人脸图片到指定文件夹, 并提取特征数据。
    返回 (提取到的特征数据, 保存的照片文件名)。
    """
    photo_filename = f"{uuid.uuid4()}.jpg"
    image_path = os.path.join(upload_folder, photo_filename)
    try:
        image_file.save(image_path)
        print(f"照片已保存到: {image_path}")
    except Exception as e:
        print(f"保存照片失败: {e}")
        return None, None # 保存失败则返回 None

    # 调用内部函数提取特征数据
    face_data = _extract_mock_face_data(image_file)
    return face_data, photo_filename

# 用于签到：仅提取特征数据，不保存照片
def extract_face_data_without_saving(image_file):
    """
    处理上传的人脸图片, 仅提取特征数据，不保存原始图片。
    返回提取到的特征数据 (模拟为字符串)。
    """
    return _extract_mock_face_data(image_file)

# Database interaction functions
def compare_stored_faces(uploaded_face_data):
    try:
        # This is still a mock comparison, in reality, you'd iterate and compare face_data
        first_user = User.query.first()
        if first_user:
            print(f"模拟人脸比对：上传特征 {uploaded_face_data}。假定与用户 {first_user.name} ({first_user.id}) 的存储特征 {first_user.face_data} 匹配成功。")
            return first_user.id
        return None
    except SQLAlchemyError as e:
        print(f"数据库查询错误 (compare_stored_faces): {e}")
        return None

def add_user(name, face_data, photo_filename):
    new_user_instance = User(name=name, face_data=face_data, photo_filename=photo_filename)
    try:
        db.session.add(new_user_instance)
        db.session.commit()
        # new_user_instance.id will be populated after commit if it's a default like UUID
        print(f"用户 {name} 已添加到数据库, ID: {new_user_instance.id}")
        return new_user_instance.id, new_user_instance.name
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"添加用户到数据库失败: {e}")
        return None, None

def find_user_by_id(user_id):
    try:
        return User.query.get(user_id)
    except SQLAlchemyError as e:
        print(f"查询用户失败 (ID: {user_id}): {e}")
        return None

def delete_user_by_id(user_id, upload_folder):
    user_to_delete = find_user_by_id(user_id)
    if user_to_delete:
        photo_path = None
        if user_to_delete.photo_filename:
            photo_path = os.path.join(upload_folder, user_to_delete.photo_filename)
        
        try:
            db.session.delete(user_to_delete) # Associated AttendanceRecords will be handled by cascade
            db.session.commit()
            print(f"用户 (ID: {user_id}) 已从数据库删除。")
            if photo_path and os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                    print(f"已删除照片文件: {photo_path}")
                except OSError as e_os:
                    print(f"删除照片文件失败: {photo_path}, 错误: {e_os}")
            return True
        except SQLAlchemyError as e_db:
            db.session.rollback()
            print(f"从数据库删除用户失败 (ID: {user_id}): {e_db}")
            return False
    return False

def add_attendance_record(user_id, user_name=None): # user_name is not strictly needed if fetching from User table
    user = find_user_by_id(user_id)
    if not user:
        print(f"添加签到记录失败：未找到用户ID {user_id}")
        return None

    new_record = AttendanceRecord(user_id=user_id, timestamp=datetime.utcnow())
    try:
        db.session.add(new_record)
        db.session.commit()
        print(f"为用户ID {user_id} 添加了签到记录, 时间: {new_record.timestamp}")
        return new_record.timestamp
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"添加签到记录到数据库失败: {e}")
        return None

def get_all_attendance_records():
    try:
        records_with_user = db.session.query(
                AttendanceRecord.id, 
                AttendanceRecord.user_id, 
                User.name.label('user_name'), 
                AttendanceRecord.timestamp
            ).join(User, AttendanceRecord.user_id == User.id)\
             .order_by(AttendanceRecord.timestamp.desc())\
             .all()
        
        formatted_records = [
            {
                'id': rec.id,
                'user_id': rec.user_id,
                'name': rec.user_name,
                'timestamp': rec.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for rec in records_with_user
        ]
        return formatted_records
    except SQLAlchemyError as e:
        print(f"获取所有签到记录失败: {e}")
        return []

def get_all_users_summary():
    try:
        users = User.query.all()
        return [
            {'id': user.id, 'name': user.name, 'photo_filename': user.photo_filename}
            for user in users
        ]
    except SQLAlchemyError as e:
        print(f"获取所有用户摘要失败: {e}")
        return [] 