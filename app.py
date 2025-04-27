# A Simple Flask API 
# Step 1 is pip install flask
 

from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Flask"

if __name__=="__main__":
    app.run(debug=True)

