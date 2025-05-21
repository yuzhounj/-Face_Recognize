from flask import Blueprint, request, jsonify, current_app
from utils import admin_required
import data_store

user_bp = Blueprint('user', __name__, url_prefix='/user') # 添加了 url_prefix

@user_bp.route('/register', methods=['POST'])
def register_user_route(): 
    if 'name' not in request.form or 'photo' not in request.files:
        return jsonify(message="缺少姓名或照片文件"), 400

    name = request.form['name']
    photo_file = request.files['photo']

    if photo_file.filename == '':
        return jsonify(message="未选择照片文件"), 400

    face_data = data_store.process_face_to_extract_data(photo_file)
    if not face_data:
        return jsonify(message="人脸数据提取失败"), 500

    user_id, user_name = data_store.add_user(name, face_data)
    return jsonify(message="用户注册成功，已存储人脸数据", user_id=user_id, name=user_name), 201

@user_bp.route('/<string:user_id>', methods=['DELETE'])
@admin_required
def delete_user_route(user_id): # 函数名修改
    if data_store.delete_user_by_id(user_id):
        return jsonify(message="用户注销成功", user_id=user_id), 200
    else:
        return jsonify(message="未找到该用户或删除失败"), 404

@user_bp.route('/list', methods=['GET'])
@admin_required
def list_all_users_route():
    """管理员查看所有已注册用户列表 (仅 ID 和姓名)"""
    users_summary = data_store.get_all_users_summary()
    return jsonify(users=users_summary), 200 