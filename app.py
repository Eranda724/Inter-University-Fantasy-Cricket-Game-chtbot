from flask import Flask, request, jsonify, render_template
import json
from fuzzywuzzy import process

app = Flask(__name__)

# Load player data from JSON file
with open('data.json', 'r') as file:
    players = json.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message", "").lower()
    
    if "player list" in user_input:
        response = [
            f"{i+1}. {p['Name']} - {p['University']} - {p['Category']} - ${p['Value']}"
            for i, p in enumerate(players) if p['Value'] is not None
        ]
        return jsonify({"response": "\n".join(response)})
    
    if "batsman" in user_input.lower():
        response = [
            f"{i+1}. {p['Name']} - {p['University']} - {p['Category']} - ${p['Value']}"
            for i, p in enumerate(players)
            if p['Category'].lower() == "batsman" and p['Value'] is not None
        ]
        return jsonify({"response": "\n".join(response) if response else "No batsmen found."})

    if user_input.isdigit():
        index = int(user_input) - 1
        if 0 <= index < len(players):
            p = players[index]
            response = (
                f"{p['Name']} from {p['University']} in {p['Category']} category "
                f"costs ${p['Value']} with {p['Player Points']} points"
            )
        else:
            response = "Invalid player index."
        return jsonify({"response": response})
    
    if "best player" in user_input:
        valid_players = [p for p in players if p.get("Player Points") is not None]
        best_player = max(valid_players, key=lambda p: p.get("Player Points", 0))
        worst_player = min(valid_players, key=lambda p: p.get("Player Points", 0))
        response = (
            f"Best Player: {best_player['Name']} - {best_player['Player Points']} points\n"
            f"Worst Player: {worst_player['Name']} - {worst_player['Player Points']} points"
        )
        return jsonify({"response": response})
    
    return jsonify({"response": "I didn't understand. Try asking about player lists or best player."})

if __name__ == '__main__':
    app.run(debug=True)
