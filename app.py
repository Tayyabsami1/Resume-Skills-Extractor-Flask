# A Simple Flask API 
# Step 1 is pip install flask
 
# Render Template will tell flask to look in templates folder for exact .html file
from flask import Flask,render_template
# This will protect us from injections 
from markupsafe import escape
app = Flask(__name__)

@app.route('/')
def base():
    return render_template('Home.html')

@app.route('/about')
def Home():
    return render_template('About.html')

@app.route('/contact')
def Contact():
    return render_template('Contact.html')

@app.route('/<name>')
def NamePage(name):
    return f"<h1>Hello , {escape(name)}</h1> "

@app.route('/id/<int:post_id>')
def IdPage(post_id):
    return f"Hello , {escape(post_id)} "



if __name__=="__main__":
    app.run(debug=True)

