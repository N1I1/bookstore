import csv

# 输入文件
input_file = './test/booktag.csv'
# 输出文件
tag_file = './test/tag.csv'
book_tag_file = './test/book_tag.csv'

# 1. 读取原始数据，收集所有tag
tags_set = set()
book_tag_rows = []

with open(input_file, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tag = row['tag'].strip()
        book_id = int(row['book_id'])
        tags_set.add(tag)
        book_tag_rows.append((book_id, tag))

# 2. 为每个tag分配tag_id
tags_list = sorted(tags_set)
tag2id = {tag: idx+1 for idx, tag in enumerate(tags_list)}

# 3. 写tag.csv
with open(tag_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['tag_id', 'name'])
    for tag, tag_id in tag2id.items():
        writer.writerow([tag_id, tag])

# 4. 写book_tag.csv
with open(book_tag_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['book_id', 'tag_id'])
    for book_id, tag in book_tag_rows:
        writer.writerow([book_id, tag2id[tag]])
