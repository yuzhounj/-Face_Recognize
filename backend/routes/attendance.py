from flask import Blueprint, request, jsonify, current_app
from utils import admin_required
import data_store

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance') # 添加了 url_prefix

@attendance_bp.route('/sign', methods=['POST'])
def sign_in_route(): 
    if 'photo' not in request.files:
        return jsonify(message="缺少签到照片文件"), 400

    photo_file = request.files['photo']
    if photo_file.filename == '':
        return jsonify(message="未选择签到照片文件"), 400
    
    # upload_folder = current_app.config['UPLOAD_FOLDER'] # 不一定需要，取决于 process_face_to_extract_data 的实现
    # uploaded_photo_filename = data_store.process_face(photo_file, upload_folder)
    # if not uploaded_photo_filename:
    #     return jsonify(message="照片处理失败"), 500

    # 为签到照片提取特征数据
    uploaded_face_data = data_store.process_face_to_extract_data(photo_file)
    if not uploaded_face_data:
        return jsonify(message="签到照片人脸数据提取失败"), 500

    # matched_user_id = data_store.compare_faces(uploaded_photo_filename, upload_folder)
    matched_user_id = data_store.compare_stored_faces(uploaded_face_data)

    if matched_user_id:
        matched_user = data_store.find_user_by_id(matched_user_id)
        if matched_user:
            timestamp = data_store.add_attendance_record(matched_user_id, matched_user['name'])
            # 可选：删除上传的临时签到照片 (如果 process_face_to_extract_data 中有保存文件的步骤)
            # 如果 process_face_to_extract_data 只是提取数据而不保存，则此处无需删除
            # uploaded_photo_path = os.path.join(upload_folder, uploaded_photo_filename) # filename 不再直接可用
            # if os.path.exists(uploaded_photo_path):
            #     os.remove(uploaded_photo_path)
            return jsonify(message=f"用户 {matched_user['name']} 签到成功", user_id=matched_user_id, timestamp=timestamp), 200
        else:
            return jsonify(message="签到失败：匹配到的用户不存在"), 500 #理论上不应发生
    else:
        # 可选：删除上传的临时签到照片 (同上)
        # uploaded_photo_path = os.path.join(upload_folder, uploaded_photo_filename)
        # if os.path.exists(uploaded_photo_path):
        #     os.remove(uploaded_photo_path)
        return jsonify(message="签到失败：未匹配到用户"), 404

@attendance_bp.route('/records', methods=['GET'])
@admin_required
def get_attendance_records_route(): 
    records = data_store.get_all_attendance_records()
    return jsonify(records=records), 200 