from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates')

app.config['NOTICES_PER_PAGE'] = 20  # 한 페이지에 표시할 공지사항 수 설정
DATABASE = os.path.join(os.path.dirname(__file__), 'data', 'database.db')


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def format_datetime(value):
    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')

app.jinja_env.filters['format_datetime'] = format_datetime

def is_admin(ip):
    # 항상 어드민으로 인식
    return True


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # 어드민 권한 확인 로직을 주석 처리 또는 삭제
        # if is_admin(request.remote_addr):
        title = request.form['title']
        content = request.form['content']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO notices (title, content) VALUES (?, ?)", (title, content))
        db.commit()
        return redirect(url_for('admin'))
        # else:
        #     return "Permission denied"

    return render_template('admin.html')


@app.route('/notices')
def notices():
    page = request.args.get('page', 1, type=int)  # 현재 페이지 번호 가져오기
    per_page = app.config['NOTICES_PER_PAGE']  # 페이지당 공지사항 수

    db = get_db()
    cursor = db.cursor()

    # 공지사항 총 개수 가져오기
    cursor.execute("SELECT COUNT(*) FROM notices")
    total_notices = cursor.fetchone()[0]

    # 페이지 번호와 페이지당 공지사항 수를 사용하여 공지사항 목록 조회
    offset = (page - 1) * per_page
    cursor.execute("SELECT * FROM notices ORDER BY id DESC LIMIT ? OFFSET ?", (per_page, offset))
    notices = cursor.fetchall()

    return render_template('notices.html', notices=notices, page=page, per_page=per_page, total_notices=total_notices)



@app.route('/notice/<int:id>')
def notice(id):
    try:
        id = int(id)  # ID를 정수로 변환 시도
    except ValueError:
        return "Invalid ID"

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM notices WHERE id=?", (id,))
    notice = cursor.fetchone()
    if notice:
        notice_dict = {
            'id': notice[0],
            'title': notice[1],
            'content': notice[2]
        }
        return render_template('notice.html', notice=notice_dict)




if __name__ == '__main__':
    app.run(debug=True)
