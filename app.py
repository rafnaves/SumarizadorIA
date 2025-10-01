import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import fitz


app = Flask(__name__)
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada no .env")

genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')




@app.route("/")
def index():
    return render_template("index.html")


@app.route('/resumir', methods=['POST'])



@app.route('/resumir-pdf', methods=['POST'])


# if __name__ == '__main__':
#     app.run(debug=True)