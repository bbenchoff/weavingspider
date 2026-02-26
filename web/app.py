import os
import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'bohemian_grove.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()

    members = cur.execute(
        'SELECT name, camp, employer, employer_title, employer_source, '
        'political_donations, opensecrets_url, ngos, notes '
        'FROM members ORDER BY camp, name'
    ).fetchall()

    total = len(members)
    with_employer = sum(1 for m in members if m['employer'])
    with_donations = sum(1 for m in members if m['political_donations'])
    camps = sorted(set(m['camp'] for m in members if m['camp']))
    num_camps = len(camps)

    conn.close()

    return render_template(
        'index.html',
        members=members,
        camps=camps,
        total=total,
        with_employer=with_employer,
        with_donations=with_donations,
        num_camps=num_camps,
    )


if __name__ == '__main__':
    app.run(debug=True)
