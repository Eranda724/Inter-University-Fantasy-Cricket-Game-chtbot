import streamlit as st
import json
import fuzzywuzzy.process as process

# Load player data from JSON file
with open('data.json', 'r') as file:
    players = json.load(file)

# Title of the app
st.title("Player Chatbot")

STANDARD_TERMS = ["batsman", "bowler", "all-rounder"]

def get_best_match(user_input, choices, threshold=70):
    """
    Finds the best match for the user input from a list of choices.
    Returns the match if the similarity score is above the threshold, otherwise None.
    """
    match, score = process.extractOne(user_input, choices)
    return match if score >= threshold else None

# Title of the app
st.title("Player Chatbot")

# Input box for user queries
user_input = st.text_input("Ask about players...", placeholder="Type your query here...")

# Normalize input and find the best match
normalized_input = user_input.lower()
best_match = get_best_match(normalized_input, STANDARD_TERMS)

# Function to process user input
def process_query(user_input):
    user_input = user_input.lower()

    if "player list" in user_input:
        response = [
            f"{i+1}. {p['Name']} - {p['University']} - {p['Category']} - ${p['Value']}"
            for i, p in enumerate(players) if p['Value'] is not None
        ]
        return "\n".join(response) if response else "No players found."

    if best_match == "batsman":
        filtered_players = [
            f"{i+1}. {p['Name']} - {p['University']} - {p['Category']} - ${p['Value']}"
            for i, p in enumerate(players)
            if p['Category'].lower() == "batsman" and p['Value'] is not None
        ]
        return "\n".join(filtered_players) if filtered_players else "No batsmen found."

    elif best_match == "bowler":
        filtered_players = [
            f"{i+1}. {p['Name']} - {p['University']} - {p['Category']} - ${p['Value']}"
            for i, p in enumerate(players)
            if p['Category'].lower() == "bowler" and p['Value'] is not None
        ]
        return "\n".join(filtered_players) if filtered_players else "No bowlers found."

    elif best_match == "all-rounder":
        filtered_players = [
            f"{i+1}. {p['Name']} - {p['University']} - {p['Category']} - ${p['Value']}"
            for i, p in enumerate(players)
            if p['Category'].lower() == "all-rounder" and p['Value'] is not None
        ]
        return "\n".join(filtered_players) if filtered_players else "No all-rounders found."

    elif user_input.isdigit():
        index = int(user_input) - 1
        if 0 <= index < len(players):
            p = players[index]
            response = (
                f"{p['Name']} from {p['University']} in {p['Category']} category "
                f"costs ${p['Value']} with {p['Player Points']} points"
            )
        else:
            response = "Invalid player index."
        return response

    if "best player" in user_input:
        valid_players = [p for p in players if p.get("Player Points") is not None]
        best_player = max(valid_players, key=lambda p: p.get("Player Points", 0))
        worst_player = min(valid_players, key=lambda p: p.get("Player Points", 0))
        response = (
            f"Best Player: {best_player['Name']} - {best_player['Player Points']} points\n"
            f"Worst Player: {worst_player['Name']} - {worst_player['Player Points']} points"
        )
        return response

    return "I didn't understand. Try asking about player lists, batsmen, or best player."

# Display the chatbot response
if user_input:
    response = process_query(user_input)
    st.write(f"**You:** {user_input}")
    st.write(f"**Bot:** {response}")