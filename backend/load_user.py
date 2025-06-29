from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

def create_admins(user_list):
    app = create_app()
    with app.app_context():
        for user_info in user_list:
            username = user_info["username"]
            if User.query.filter_by(username=username).first():
                print(f"User '{username}' already exists, skipping.")
                continue
            hashed_password = generate_password_hash(user_info["password"])
            user = User(
                username=username,
                password=hashed_password,
                email=user_info["email"],
                phone=user_info["phone"]
            )
            db.session.add(user)
            print(f"User '{username}' created.")
        db.session.commit()
        print("All user processed.")

if __name__ == "__main__":
    users = [
        {
            "username": "user1",
            "password": "user123",
            "email": "he231920@outlook.com",
            "phone": "12345678901"
        },
        {
            "username": "user2",
            "password": "user456",
            "email": "2148741639@qq.com",
            "phone": "12345678902"
        },
        {
            "username": "user3",
            "password": "user789",
            "email": "2290545236@qq.com",
            "phone": "12345678903"
        }
    ]
    create_admins(users)
