import os
import uuid
from datetime import datetime
import json # 用于序列化和反序列化面部编码列表
import numpy as np # 用于处理面部编码数组
import face_recognition # 主要的人脸识别库

from models import db, User, AttendanceRecord # From models.py
from sqlalchemy.exc import SQLAlchemyError

# --- Private Helper Function for Face Encoding Extraction ---
def _extract_face_encoding(image_file_stream):
    """(Internal) 从图片文件流中提取第一个检测到的人脸编码。
    
    Args:
        image_file_stream: werkzeug.datastructures.FileStorage object (上传的文件对象)
    
    Returns:
        str: JSON 字符串表示的人脸编码 (128个浮点数的列表)，如果找到人脸。
        None: 如果没有检测到人脸或发生错误。
    """
    try:
        # face_recognition.load_image_file可以直接处理文件流或文件路径
        # 为了确保它能正确处理 FileStorage 对象，最好先读取其内容
        # image_file_stream.seek(0) # 确保从文件开头读取
        # image = face_recognition.load_image_file(image_file_stream)
        
        # 更直接的方式是 FileStorage 对象通常有一个 `stream` 属性或可以直接传递
        # 但最安全的是先保存到临时位置或读取到内存中给 face_recognition
        # 为简单起见，我们假设 face_recognition.load_image_file 可以处理它
        # 如果不行，需要 image_file_stream.read() 然后用 BytesIO 包装，或者临时保存
        image_file_stream.seek(0) # 重置文件指针到开头，以防之前被读取过
        image = face_recognition.load_image_file(image_file_stream)
        
        face_encodings = face_recognition.face_encodings(image) # 返回一个包含所有检测到人脸编码的列表

        if face_encodings: # 如果检测到了人脸
            if len(face_encodings) > 1:
                print(f"警告：在图片中检测到 {len(face_encodings)} 张人脸。将使用第一张。")
            first_face_encoding = face_encodings[0] # 取第一个人脸的编码
            # 将 numpy 数组转换为列表，然后序列化为 JSON 字符串
            return json.dumps(first_face_encoding.tolist())
        else:
            print("未在图片中检测到人脸。")
            return None
    except Exception as e:
        print(f"提取人脸编码时出错: {e}")
        return None

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
    # image_file 在被 image_file.save() 后，其文件指针可能在末尾，需要重置
    image_file.seek(0)
    face_encoding_json = _extract_face_encoding(image_file)
    return face_encoding_json, photo_filename # face_encoding_json 可能是 None

# 用于签到：仅提取特征数据，不保存照片
def extract_face_data_without_saving(image_file):
    """
    处理上传的人脸图片, 仅提取特征数据，不保存原始图片。
    返回提取到的特征数据 (模拟为字符串)。
    """
    return _extract_face_encoding(image_file) # face_encoding_json 可能是 None

# Database interaction functions
def compare_stored_faces(uploaded_face_encoding_json):
    """
    将上传照片提取的特征编码与数据库中所有用户的特征编码进行比对。
    Args:
        uploaded_face_encoding_json (str): JSON 字符串表示的待比对人脸编码。
    Returns:
        str: 匹配到的用户ID，如果未匹配到则返回 None。
    """
    if not uploaded_face_encoding_json:
        return None

    try:
        uploaded_encoding_list = json.loads(uploaded_face_encoding_json)
        uploaded_encoding = np.array(uploaded_encoding_list)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"解析上传的人脸编码时出错: {e}")
        return None

    try:
        all_users = User.query.all()
        if not all_users:
            print("数据库中没有用户可供比对。")
            return None

        known_face_encodings = []
        user_ids_ordered = []

        for user in all_users:
            if user.face_data:
                try:
                    stored_encoding_list = json.loads(user.face_data)
                    known_face_encodings.append(np.array(stored_encoding_list))
                    user_ids_ordered.append(user.id)
                except (json.JSONDecodeError, TypeError):
                    print(f"解析用户 {user.id} 的存储面部数据时出错，跳过此用户。")
                    continue # 跳过这个损坏的数据
            else:
                print(f"用户 {user.id} 没有面部数据，跳过此用户。")

        if not known_face_encodings:
            print("数据库中没有有效的已知人脸编码可供比对。")
            return None

        #进行比较
        # compare_faces 返回一个布尔值列表，表示 known_face_encodings中的每个编码是否与 uploaded_encoding 匹配
        matches = face_recognition.compare_faces(known_face_encodings, uploaded_encoding, tolerance=0.6) # tolerance可以调整

        for i, match in enumerate(matches):
            if match:
                matched_user_id = user_ids_ordered[i]
                print(f"人脸匹配成功: 上传的人脸与用户ID {matched_user_id} 匹配。")
                return matched_user_id
        
        print("未找到匹配的人脸。")
        return None

    except SQLAlchemyError as e:
        print(f"数据库查询错误 (compare_stored_faces): {e}")
        return None
    except Exception as e:
        print(f"在 compare_stored_faces 中发生意外错误: {e}")
        return None

def add_user(name, face_data_json, photo_filename): # face_data 现在是 JSON string
    if not face_data_json: # 如果提取编码失败，不应添加用户
        print(f"尝试添加用户 {name} 失败，因为人脸数据为空。")
        return None, None
        
    new_user_instance = User(name=name, face_data=face_data_json, photo_filename=photo_filename)
    try:
        db.session.add(new_user_instance)
        db.session.commit()
        print(f"用户 {name} 已添加到数据库, ID: {new_user_instance.id}, FaceDataStored: {'Yes' if face_data_json else 'No'}")
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