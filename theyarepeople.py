from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy

import os
import datetime
from dateutil.tz import tzlocal

app = Flask(__name__)
db = SQLAlchemy(app)

entries = ['David Barstow, \"Donald Trump\'s Election Office and Unlikely Melting Pot\", New York Times, March 13, 2016']*20 # eventually, pull from db
# So it's ~14 double-liners, or 24 singles

# entries = db.Submission.query.all()
# left = entries[:14]
# right = entries[14:28]
# middle = entries[28:]

local = app.root_path == '/Users/alexloewi/Documents/Sites/theyarepeople'

if local:
    db_url = "postgres://alexloewi:"+os.environ['LOCAL_DB_PWD']+"@localhost:5432/theyarepeople"
    app.config['TESTING'] = True # DISTINCT from 'debug,' removes password locks
else:
    db_url = os.environ['DATABASE_URL'] # is fine on heroku
#'sqlite:////tmp/test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url



class Submission(db.Model):
    __tablename__ = "submission"

    """Data and metadata on entries sent from the textfield.
    """
    id    = db.Column(db.Integer, primary_key=True)
    text  = db.Column(db.Text)
    stamp = db.Column(db.DateTime)
    # location -- ? how to store that?

    def __init__(self, text):
        self.text = text
        self.stamp = datetime.datetime.now(tzlocal())
        # self.location = whatever ... lat, long?



@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'POST':

        submission = Submission(request.form['text']) # I also want datetime, and ... sending IP.
        db.session.add(submission)
        db.session.commit()

    return render_template('theyarepeople.html', entries=entries) #left=left, middle=middle, right=right)


if __name__ == "__main__":
    # Thanks, stx (again)
    # Bind to PORT if defined, otherwise default to 5001.
    port = int(os.environ.get('PORT', 5001))
    debug = app.root_path == '/Users/alexloewi/Documents/Sites/theyarepeople'
    db.create_all()
    app.run(host='0.0.0.0', port=port, debug=debug)
