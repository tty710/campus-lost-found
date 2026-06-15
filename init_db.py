"""
校园失物招领平台 — 初始化脚本
运行此脚本创建数据库并设置管理员账号
"""
from app import create_app
from models import db, User

app = create_app()

with app.app_context():
    db.create_all()
    print("数据库表已创建")

    # 创建默认管理员
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(username="admin", email="admin@campus.edu", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("默认管理员已创建: admin / admin123")
    else:
        print("管理员账号已存在，跳过")

    # 创建测试用户
    user = User.query.filter_by(username="testuser").first()
    if not user:
        user = User(username="testuser", email="test@campus.edu", phone="13800138000")
        user.set_password("123456")
        db.session.add(user)
        db.session.commit()
        print("测试用户已创建: testuser / 123456")

    print("\n初始化完成！运行 python app.py 启动服务")
    print("访问 http://localhost:5000")
