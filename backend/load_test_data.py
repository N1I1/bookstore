# load_books.py
import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from app.models import Book, BookTag
from app import db

# 数据库连接信息
DATABASE_URI = f"mysql+pymysql://{Config.USERNAME}:{Config.PASSWORD}@{Config.HOST}:{Config.PORT}/{Config.DBNAME}"

# 创建数据库引擎
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def load_books_from_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # 创建 Book 对象
            book = Book(
                book_id=row['book_id'],
                title=row['title'],
                author=row['author'],
                isbn=row['isbn'],
                publisher=row['publisher'],
                price=row['price'],
                discount=row['discount'],
                stock=row['stock'],
                description=row['description'],
                image_url=row['image_url']  # 添加 image_url 字段
            )
            session.add(book)
    session.commit()
    print("书籍数据加载完成！")

def load_book_tags_from_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # 创建 BookTag 对象
            book_tag = BookTag(
                book_tag_id=row['book_tag_id'],
                book_id=row['book_id'],
                tag=row['tag']
            )
            session.add(book_tag)
    session.commit()
    print("书籍标签数据加载完成！")

if __name__ == '__main__':
    # 获取当前脚本的绝对路径
    current_script_path = os.path.abspath(__file__)
    # 获取当前脚本所在的目录
    current_script_dir = os.path.dirname(current_script_path)
    # 拼接数据文件夹路径
    data_folder = os.path.join(current_script_dir, 'data\\test')

    # 拼接文件路径
    book_file_path = os.path.join(data_folder, 'book.csv')
    booktag_file_path = os.path.join(data_folder, 'booktag.csv')

    # 检查文件是否存在
    if not os.path.exists(book_file_path):
        raise FileNotFoundError(f"文件不存在: {book_file_path}")
    if not os.path.exists(booktag_file_path):
        raise FileNotFoundError(f"文件不存在: {booktag_file_path}")

    # 加载书籍数据
    load_books_from_csv(book_file_path)
    # 加载书籍标签数据
    load_book_tags_from_csv(booktag_file_path)
