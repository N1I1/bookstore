import os
import time
import datetime
import subprocess
import glob

DB_USER = "root"
DB_PASS = "root"
DB_NAME = "bookstore_db"
BACKUP_DIR = "./backup"
KEEP_SECONDS = 2 * 3600  # 2小时

def backup_db():
    now = datetime.datetime.now()
    backup_file = os.path.join(
        BACKUP_DIR, f"bookstore_{now.strftime('%Y-%m-%d_%H-%M-%S')}.sql"
    )
    cmd = [
        "mysqldump",
        f"-u{DB_USER}",
        f"-p{DB_PASS}",
        DB_NAME
    ]
    with open(backup_file, "w", encoding="utf-8") as f:
        subprocess.run(cmd, stdout=f)
    print(f"[{now}] 数据库已备份到 {backup_file}")

def clean_old_backups():
    now = time.time()
    for file in glob.glob(os.path.join(BACKUP_DIR, "bookstore_*.sql")):
        if os.path.isfile(file):
            mtime = os.path.getmtime(file)
            if now - mtime > KEEP_SECONDS:
                os.remove(file)
                print(f"[{datetime.datetime.now()}] 已删除过期备份 {file}")

def main():
    print("数据库备份守护进程已启动")
    while True:
        backup_db()
        clean_old_backups()
        time.sleep(1800)  # 30分钟

if __name__ == "__main__":
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    main()
