from flask import Blueprint, request, jsonify, session
from utils import admin_required

auth_bp = Blueprint('auth', __name__, url_prefix='/auth') 

@auth_bp.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify(message="缺少用户名或密码"), 400

    username = data['username']
    password = data['password']

    if username == '123' and password == '123':
        session['admin_logged_in'] = True
        return jsonify(message="管理员登录成功"), 200
    else:
        return jsonify(message="用户名或密码错误"), 401

@auth_bp.route('/logout', methods=['POST'])
@admin_required
def admin_logout():
    session.pop('admin_logged_in', None)
    return jsonify(message="管理员登出成功"), 200 