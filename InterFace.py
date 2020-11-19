from flask import session, Flask, url_for, render_template, request, redirect

app = Flask(__name__)
app.secret_key = "skomplikowane"


@app.route('/')
def home():
    return 'Hello World'

@app.route('/main')
def main():
    return render_template('base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nm = request.form['nm']
        age = request.form['age']
        session["username"] = nm
        session["age"] = age
        if session["username"] != '':
            return redirect(url_for('name'))
    else:
        return render_template('login.html')

@app.route("/name")
def name():
    if session["username"] != None:
        usr = session["username"]
        print(type(usr),"12")
        age = session["age"]
        later = int(age)*2
        return render_template('name.html', age=age, user=usr, later=later)
    else:
        return redirect(url_for('login'))

@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("age", None)
    return redirect(url_for('login'))


@app.route('/map')
def map():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)


