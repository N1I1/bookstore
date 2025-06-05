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
    