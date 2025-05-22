from flask import Blueprint, request, jsonify, current_app, url_for
from utils import admin_required
import data_store
import os # 需要 os 来辅助删除操作中的路径检查 (虽然删除本身在 data_store)

user_bp = Blueprint('user', __name__, url_prefix='/user') # 添加了 url_prefix

@user_bp.route('/register', methods=['POST'])
def register_user_route(): 
    if 'name' not in request.form or 'photo' not in request.files:
        return jsonify(message="缺少姓名或照片文件"), 400

    name = request.form['name']
    photo_file = request.files['photo']

    if photo_file.filename == '':
        return jsonify(message="未选择照片文件"), 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    face_data, photo_filename = data_store.save_photo_and_extract_data(photo_file, upload_folder)

    if not face_data or not photo_filename:
        return jsonify(message="人脸数据提取或照片保存失败"), 500

    user_id, user_name = data_store.add_user(name, face_data, photo_filename)
    return jsonify(message="用户注册成功，已存储人脸数据和照片", user_id=user_id, name=user_name, photo_filename=photo_filename), 201

@user_bp.route('/<string:user_id>', methods=['DELETE'])
@admin_required
def delete_user_route(user_id):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    # data_store.delete_user_by_id 现在需要 upload_folder 参数
    if data_store.delete_user_by_id(user_id, upload_folder):
        return jsonify(message="用户注销成功，并已删除相关照片"), 200
    else:
        return jsonify(message="未找到该用户或删除失败"), 404

@user_bp.route('/list', methods=['GET'])
@admin_required
def list_all_users_route():
    """管理员查看所有已注册用户列表 (ID, 姓名, 照片文件名, 照片URL)"""
    users_summary_raw = data_store.get_all_users_summary()
    users_summary_with_photo_url = []
    for user_info in users_summary_raw:
        if user_info.get('photo_filename'):
            # 'serve_photo' 是我们在 app.py 中定义的函数名
            user_info['photo_url'] = url_for('serve_photo', filename=user_info['photo_filename'], _external=True)
        else:
            user_info['photo_url'] = None
        users_summary_with_photo_url.append(user_info)
    
    return jsonify(users=users_summary_with_photo_url), 200 