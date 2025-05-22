from flask import Flask, jsonify, send_from_directory
from models import db # 从 models.py 导入 db 对象
import os

# 应用工厂模式
def create_app():
    app = Flask(__name__, static_folder='../uploads', static_url_path='/user_photos')

    # 从 config.py 加载配置
    app.config.from_pyfile('config.py') # 或者 app.config.from_object('config')

    # 初始化 SQLAlchemy
    db.init_app(app) # 将 db 对象与 Flask app 实例关联

    # 在应用上下文中创建数据库表 (如果它们还不存在)
    # 这是一个简单的方法，适用于开发。对于生产，通常使用迁移工具如 Flask-Migrate。
    with app.app_context():
        db.create_all()
        print("数据库表已检查/创建 (如果不存在)。")

    # 确保 UPLOAD_FOLDER 配置可用
    upload_folder_name = app.config.get('UPLOAD_FOLDER', 'uploads') # 从配置获取，默认为 'uploads'
    
    # 更健壮的静态文件夹配置方式：
    from flask import send_from_directory # 需要导入
    import os # 需要导入

    @app.route('/uploads/<path:filename>')
    def serve_photo(filename):
        # upload_dir = app.config['UPLOAD_FOLDER'] # 这是相对路径名，例如 'uploads'
        # directory = os.path.join(app.root_path, upload_dir) # 构建绝对路径
        # 如果 UPLOAD_FOLDER 在 config.py 中已经是绝对路径，则直接使用
        upload_folder_config = app.config.get('UPLOAD_FOLDER')
        if not upload_folder_config:
            return "UPLOAD_FOLDER not configured", 500
        
        if not os.path.isabs(upload_folder_config):
            directory = os.path.join(app.root_path, upload_folder_config)
        else:
            directory = upload_folder_config
            
        return send_from_directory(directory, filename)

    # 注册蓝图
    from routes.auth import auth_bp
    from routes.user import user_bp
    from routes.attendance import attendance_bp

    app.register_blueprint(auth_bp)  # 已经在 auth.py 中设置 url_prefix='/auth'
    app.register_blueprint(user_bp)  # 已经在 user.py 中设置 url_prefix='/user'
    app.register_blueprint(attendance_bp) # 已经在 attendance.py 中设置 url_prefix='/attendance'

    @app.route('/')
    def hello_world():
        return jsonify(message='人脸签到系统后端正在运行! Modularized. DB Ready.'), 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True) # 开启 debug 模式方便调试
