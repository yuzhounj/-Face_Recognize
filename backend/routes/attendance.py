from flask import Blueprint, request, jsonify, current_app
from utils import admin_required
import data_store

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/sign', methods=['POST'])
def sign_in_route():
    if 'photo' not in request.files:
        return jsonify(message="缺少签到照片文件"), 400

    photo_file = request.files['photo']
    if photo_file.filename == '':
        return jsonify(message="未选择签到照片文件"), 400
    
    uploaded_face_data = data_store.extract_face_data_without_saving(photo_file)
    
    if not uploaded_face_data:
        return jsonify(message="签到照片人脸数据提取失败"), 500

    matched_user_id = data_store.compare_stored_faces(uploaded_face_data)

    if matched_user_id:
        matched_user = data_store.find_user_by_id(matched_user_id) # matched_user is a User object
        if matched_user:
            # 不再需要传递 matched_user.name，因为 add_attendance_record 可以通过 user_id 关联
            # timestamp = data_store.add_attendance_record(matched_user_id, matched_user.name)
            timestamp = data_store.add_attendance_record(matched_user_id)
            if timestamp: # 检查 add_attendance_record 是否成功
                return jsonify(message=f"用户 {matched_user.name} 签到成功", user_id=matched_user_id, timestamp=timestamp.strftime("%Y-%m-%d %H:%M:%S")), 200
            else:
                return jsonify(message=f"用户 {matched_user.name} 签到失败，无法记录签到数据"), 500
        else:
            return jsonify(message="签到失败：匹配到的用户在数据库中不存在"), 500 # 理论上不应发生，因为 matched_user_id 来自数据库
    else:
        return jsonify(message="签到失败：未匹配到用户"), 404

@attendance_bp.route('/records', methods=['GET'])
@admin_required
def get_attendance_records_route(): 
    records = data_store.get_all_attendance_records()
    return jsonify(records=records), 200 