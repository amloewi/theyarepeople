from flask import Flask, render_template

import os

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('theyarepeople.html')

if __name__ == "__main__":
    # Thanks, stx (again)
    # Bind to PORT if defined, otherwise default to 5001.
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
