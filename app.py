# A Simple Flask API 
# Step 1 is pip install flask
 

from flask import Flask
app = Flask(__name__)

@app.route('/')
def base():
    return "<h1>Hello From Flask"

@app.route('/home')
def Home():
    return "<h1>I am Home page<h1>"

if __name__=="__main__":
    app.run(debug=True)

