import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config
from app.models import Book, book_tag
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
                image_url=row['image_url']
            )
            session.add(book)
    session.commit()
    print("书籍数据加载完成！")

def load_book_tags_from_csv(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # 直接插入到 book_tag 关联表
            session.execute(
                book_tag.insert().values(
                    book_id=row['book_id'],
                    tag_id=row['tag_id']
                )
            )
    session.commit()
    print("书籍标签关联数据加载完成！")

def load_tags_from_csv(file_path):
    import csv
    from app.models import Tag

    with open(file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            tag = Tag(
                tag_id=row['tag_id'],
                name=row['name']
            )
            session.add(tag)
    session.commit()
    print("标签数据加载完成！")

if __name__ == '__main__':
    # 获取当前脚本的绝对路径
    current_script_path = os.path.abspath(__file__)
    current_script_dir = os.path.dirname(current_script_path)
    data_folder = os.path.join(current_script_dir, 'data', 'test')

    book_file_path = os.path.join(data_folder, 'book.csv')
    booktag_file_path = os.path.join(data_folder, 'book_tag.csv')
    tag_file_path = os.path.join(data_folder, 'tag.csv')

    if not os.path.exists(tag_file_path):
        raise FileNotFoundError(f"文件不存在: {tag_file_path}")
    if not os.path.exists(book_file_path):
        raise FileNotFoundError(f"文件不存在: {book_file_path}")
    if not os.path.exists(booktag_file_path):
        raise FileNotFoundError(f"文件不存在: {booktag_file_path}")
    load_tags_from_csv(tag_file_path)
    load_books_from_csv(book_file_path)
    load_book_tags_from_csv(booktag_file_path)
