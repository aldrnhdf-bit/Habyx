from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['password'] == "12345":
            return "Login Successful!"
        return "Login Failed"
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)