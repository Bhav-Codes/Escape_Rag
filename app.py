from flask import Flask, request, jsonify
from src.main import run_pipeline  # your existing function

app = Flask(__name__)

@app.route("/hackrx/run", methods=["POST"])
def run_hackrx():
    data = request.get_json()  # Read incoming JSON
    documents = data.get("documents")
    questions = data.get("questions")

    result = run_pipeline(documents, questions)

    return jsonify({"answers": result})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)