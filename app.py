from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import pandas as pd
from flask import send_file
import io


app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Database Table
class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    site = db.Column(db.String(100))
    entry_time = db.Column(db.String(50))
    exit_time = db.Column(db.String(50))
    date = db.Column(db.String(50))


@app.route('/', methods=['GET','POST'])
def index():
    
    if request.method == 'POST':
        name = request.form['name']
        site = request.form['site']
        entry_time = request.form['entry_time']
        exit_time = request.form['exit_time']

        record = Attendance(
            name=name,
            site=site,
            entry_time=entry_time,
            exit_time=exit_time,
            date=str(datetime.today().date())
        )

        db.session.add(record)
        db.session.commit()

        return redirect('/')

    records = Attendance.query.all()

    return render_template('index.html', records=records)
@app.route('/delete/<int:id>')
def delete(id):

    record = Attendance.query.get_or_404(id)

    db.session.delete(record)
    db.session.commit()

    return redirect('/')


# EDIT ATTENDANCE
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    record = Attendance.query.get_or_404(id)

    if request.method == 'POST':

        record.name = request.form['name']
        record.site = request.form['site']
        record.entry_time = request.form['entry_time']
        record.exit_time = request.form['exit_time']

        db.session.commit()

        return redirect('/')
return render_template('edit.html', record=record)


@app.route("/daily-report")
def daily_report():
    today = date.today().strftime("%Y-%m-%d")
    records = Attendance.query.filter_by(date=today).all()
    
    return render_template("daily_report.html", records=records)
    @app.route("/download-report")
def download_report():
    today = date.today().strftime("%Y-%m-%d")
    records = Attendance.query.filter_by(date=today).all()

    import pandas as pd
    import io
    from flask import send_file

    data = []
    for r in records:
        data.append({
            "Name": r.name,
            "Site": r.site,
            "Entry": r.entry_time,
            "Exit": r.exit_time,
            "Date": r.date
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)

    return send_file(output,
                     download_name="daily_attendance.xlsx",
                     as_attachment=True)
 

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')



