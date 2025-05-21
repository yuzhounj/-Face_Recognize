import uuid
# import os # os.path.join 和 image_file.save 不再需要直接在此函数中使用
from datetime import datetime

# 本地缓存
users_db = []  # 存储用户信息, e.g., [{'id': 'uuid', 'name': '张三', 'face_data': 'mock_feature_vector_xxxx'}]
attendance_records_db = []  # 存储签到记录, e.g., [{'user_id': 'uuid', 'name': '张三', 'timestamp': 'YYYY-MM-DD HH:MM:SS'}]



# 模拟人脸数据提取的函数
def process_face_to_extract_data(image_file):
    """
    处理上传的人脸图片, 提取特征数据。
    在这个阶段，我们不保存原始图片，而是模拟提取特征数据。
    实际应用中，这里会调用视觉神经网络API来获取面部特征向量。
    返回提取到的特征数据 (模拟为字符串)。
    """
    # 模拟特征提取，实际中这里会是复杂的处理
    # image_file 参数仍然保留，因为实际的库会从文件对象读取数据
    mock_face_data = f"mock_feature_vector_{uuid.uuid4().hex[:10]}_for_{image_file.filename}"
    print(f"模拟人脸数据提取：为图片 '{image_file.filename}' 生成特征数据: {mock_face_data}")
    return mock_face_data

# 模拟人脸比对函数
def compare_stored_faces(uploaded_face_data):
    """
    模拟人脸比对。
    将上传照片提取的特征数据 (uploaded_face_data) 与数据库中存储的用户特征数据进行比对。
    返回匹配到的用户ID，如果未匹配到则返回 None。
    """
    if not users_db:
        return None
    
    # ！！！重要提示！！！
    # 这是一个非常简化的模拟。
    # 您需要在此处实现真实的人脸识别和比对逻辑，
    # 比如计算 uploaded_face_data 和每个 user['face_data'] 之间的相似度。
    # for user in users_db:
    #     similarity = calculate_similarity(uploaded_face_data, user['face_data'])
    #     if similarity > THRESHOLD:
    #         print(f"模拟人脸比对：上传特征 {uploaded_face_data} 与用户 {user['name']} 的特征 {user['face_data']} 匹配成功。")
    #         return user['id']

    # 暂时模拟：如果数据库中有用户，就认为匹配到第一个用户
    # 注意：这种模拟方式意味着任何签到尝试都会匹配第一个注册用户（如果存在）
    # 为了演示，我们可以简单地假设它与第一个用户的特征匹配
    print(f"模拟人脸比对：上传特征 {uploaded_face_data}。假定与用户 {users_db[0]['name']} ({users_db[0]['id']}) 的存储特征 {users_db[0]['face_data']} 匹配成功。")
    return users_db[0]['id']

def add_user(name, face_data): 
    user_id = str(uuid.uuid4())
    new_user = {
        'id': user_id,
        'name': name,
        'face_data': face_data 
    }
    users_db.append(new_user)
    return user_id, name

def find_user_by_id(user_id):
    return next((user for user in users_db if user['id'] == user_id), None)

def delete_user_by_id(user_id):
    global users_db
    user_to_delete = find_user_by_id(user_id)
    if user_to_delete:
        users_db = [user for user in users_db if user['id'] != user_id]
        # 可选：删除关联的签到记录
        # global attendance_records_db
        # attendance_records_db = [record for record in attendance_records_db if record['user_id'] != user_id]
        # 注意：如果之前是根据 photo_filename 删除文件，现在已经没有文件可删了
        return True
    return False

def add_attendance_record(user_id, user_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attendance_records_db.append({
        'user_id': user_id,
        'name': user_name,
        'timestamp': timestamp
    })
    return timestamp

def get_all_attendance_records():
    return attendance_records_db

def get_all_users_summary():
    """
    获取所有已注册用户的简要信息 (ID 和姓名)。
    """
    return [{'id': user['id'], 'name': user['name']} for user in users_db] 