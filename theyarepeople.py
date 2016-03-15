from flask import Flask, render_template, request, send_from_directory
from flask.ext.sqlalchemy import SQLAlchemy

import os
import datetime
from dateutil.tz import tzlocal
from geoip import geolite2

app = Flask(__name__)
db = SQLAlchemy(app)
local = app.root_path == '/Users/alexloewi/Documents/Sites/theyarepeople'

if local:
    db_url = "postgres://alexloewi:"+os.environ['LOCAL_DB_PWD']+"@localhost:5432/theyarepeople"
    app.config['TESTING'] = True # DISTINCT from 'debug,' removes password locks
else:
    db_url = os.environ['DATABASE_URL'] # is fine on heroku
app.config['SQLALCHEMY_DATABASE_URI'] = db_url



class Submission(db.Model):
    __tablename__ = "submission"

    """Data and metadata on entries sent from the textfield.
    """
    id       = db.Column(db.Integer, primary_key=True)
    text     = db.Column(db.Text)
    stamp    = db.Column(db.DateTime)
    approved = db.Column(db.Boolean)
    ip       = db.Column(db.String(45))
    latlong  = db.Column(db.String(30))
    city     = db.Column(db.String(80))

    def __init__(self, text, ip):
        self.text     = text
        self.stamp    = datetime.datetime.now(tzlocal())
        self.approved = False

        try:
            self.ip       = ip
            match = geolite2.lookup(ip)
            self.latlong  = str(match.location[0])+","+str(match.location[1])
            self.city     = match['city']['names']['en']
        except Exception, x:
            print x

@app.route('/favicon.ico')
def favicon():
    path = os.path.join(app.root_path, 'static/images')
    return send_from_directory(path, 'favicon.ico',
                mimetype='image/vnd.microsoft.icon')

@app.route("/", methods=['GET', 'POST'])
def main():

    if request.method == 'POST':

        print request.remote_addr
        submission = Submission(request.form['text'], request.remote_addr)
        db.session.add(submission)
        db.session.commit()

    entries = [s.text for s in Submission.query.order_by(Submission.id.desc()) if s.approved]
    left = entries[:14]
    right = entries[14:28]
    middle = entries[28:]

    return render_template('theyarepeople.html', left=left, middle=middle, right=right)


if __name__ == "__main__":
    # Thanks, stx (again)
    # Bind to PORT if defined, otherwise default to 5001.
    port = int(os.environ.get('PORT', 5001))
    debug = app.root_path == '/Users/alexloewi/Documents/Sites/theyarepeople'
    #db.drop_all()
    db.create_all()
    app.run(host='0.0.0.0', port=port, debug=debug)
