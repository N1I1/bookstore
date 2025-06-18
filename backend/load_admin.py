from app import create_app, db
from app.models.admin import Admin
from werkzeug.security import generate_password_hash

def create_admins(admin_list):
    app = create_app()
    with app.app_context():
        for admin_info in admin_list:
            username = admin_info["username"]
            if Admin.query.filter_by(username=username).first():
                print(f"Admin '{username}' already exists, skipping.")
                continue
            hashed_password = generate_password_hash(admin_info["password"])
            admin = Admin(
                username=username,
                password=hashed_password,
                email=admin_info["email"],
                phone=admin_info["phone"]
            )
            db.session.add(admin)
            print(f"Admin '{username}' created.")
        db.session.commit()
        print("All admins processed.")

if __name__ == "__main__":
    admins = [
        {
            "username": "admin1",
            "password": "admin123",
            "email": "admin1@example.com",
            "phone": "12345678901"
        },
        {
            "username": "admin2",
            "password": "admin456",
            "email": "admin2@example.com",
            "phone": "12345678902"
        },
        {
            "username": "admin3",
            "password": "admin789",
            "email": "admin3@example.com",
            "phone": "12345678903"
        }
    ]
    create_admins(admins)
