from functools import wraps
from flask import session, jsonify

# 管理员登录装饰器
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify(message="管理员未登录或权限不足"), 401
        return f(*args, **kwargs)
    return decorated_function 