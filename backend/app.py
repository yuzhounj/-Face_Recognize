from flask import Flask, jsonify

# 应用工厂模式
def create_app():
    app = Flask(__name__)

    # 从 config.py 加载配置
    app.config.from_pyfile('config.py') # 或者 app.config.from_object('config')


    # 注册蓝图
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.attendance import attendance_bp


    app.register_blueprint(auth_bp)  # 已经在 auth.py 中设置 url_prefix='/auth'
    app.register_blueprint(user_bp)  # 已经在 user.py 中设置 url_prefix='/user'
    app.register_blueprint(attendance_bp) # 已经在 attendance.py 中设置 url_prefix='/attendance'

    @app.route('/')
    def hello_world():
        return jsonify(message='人脸签到系统后端正在运行! Modularized.'), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) # 开启 debug 模式方便调试
