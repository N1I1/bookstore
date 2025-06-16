import os

basedir = os.path.abspath(os.path.dirname(__file__))
class Config:
    """Base configuration class."""
    DIALECT = "mysql+pymysql"
    HOST = "127.0.0.1"
    PORT = "3306"
    USERNAME = "root"
    PASSWORD = "root"
    DBNAME = "bookstore_db"

    SQLALCHEMY_DATABASE_URI = (
        f"{DIALECT}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"
        # 'sqlite:///' +  os.path.join(basedir, 'instance', 'bookstore.db')  # Use SQLite for simplicity in this example
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'root'

    # email
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    # MAIL_USE_TLS = True
    MAIL_USERNAME = '**@qq.com'
    MAIL_PASSWORD = '**'
    MAIL_DEFAULT_SENDER = '**@qq.com'
    