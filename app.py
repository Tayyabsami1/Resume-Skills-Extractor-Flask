# A Simple Flask API 
# Step 1 is pip install flask
 

from flask import Flask
# This will protect us from injections 
from markupsafe import escape
app = Flask(__name__)

@app.route('/')
def base():
    return "<h1>Hello From Flask"

@app.route('/home')
def Home():
    return "<h1>I am Home page</h1>"

@app.route('/<name>')
def NamePage(name):
    return f"<h1>Hello , {escape(name)}</h1> "

@app.route('/id/<int:post_id>')
def IdPage(post_id):
    return f"Hello , {escape(post_id)} "



if __name__=="__main__":
    app.run(debug=True)

