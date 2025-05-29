import streamlit as st
import json
from fuzzywuzzy import process
import os

# Page configuration
st.set_page_config(
    page_title="Player Chatbot",
    page_icon="🏏",
    layout="wide"
)

# Load player data from JSON file
@st.cache_data
def load_players():
    """Load player data with caching for better performance"""
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("❌ data.json file not found. Please make sure the file exists in the same directory.")
        return []
    except json.JSONDecodeError:
        st.error("❌ Invalid JSON format in data.json file.")
        return []

players = load_players()

# Standard terms for fuzzy matching
STANDARD_TERMS = ["batsman", "bowler", "all-rounder", "player list", "best player", "worst player"]

def get_best_match(user_input, choices, threshold=60):
    """
    Finds the best match for the user input from a list of choices.
    Returns the match if the similarity score is above the threshold, otherwise None.
    """
    if not user_input.strip():
        return None
    
    match, score = process.extractOne(user_input, choices)
    return match if score >= threshold else None

def format_player_info(player, index=None):
    """Format player information consistently"""
    prefix = f"{index}. " if index is not None else ""
    value = f"${player['Value']}" if player.get('Value') is not None else "N/A"
    return f"{prefix}{player['Name']} - {player['University']} - {player['Category']} - {value}"

def get_players_by_category(category):
    """Get players filtered by category"""
    return [
        p for p in players 
        if p.get('Category', '').lower() == category.lower() and p.get('Value') is not None
    ]

def process_query(user_input):
    """Process user query and return appropriate response"""
    if not user_input.strip():
        return "Please enter a query."
    
    user_input_lower = user_input.lower().strip()
    
    # Direct matches first
    if "player list" in user_input_lower:
        valid_players = [p for p in players if p.get('Value') is not None]
        if not valid_players:
            return "No players found with valid values."
        
        response = [format_player_info(p, i+1) for i, p in enumerate(valid_players)]
        return f"📋 **Player List ({len(valid_players)} players):**\n" + "\n".join(response)
    
    # Check if input is a number (player index)
    if user_input_lower.isdigit():
        index = int(user_input_lower) - 1
        if 0 <= index < len(players):
            p = players[index]
            points = p.get('Player Points', 'N/A')
            value = f"${p['Value']}" if p.get('Value') is not None else "N/A"
            return (
                f"🏏 **Player Details:**\n"
                f"**Name:** {p['Name']}\n"
                f"**University:** {p['University']}\n"
                f"**Category:** {p['Category']}\n"
                f"**Value:** {value}\n"
                f"**Points:** {points}"
            )
        else:
            return f"❌ Invalid player index. Please enter a number between 1 and {len(players)}."
    
    # Best/Worst player queries
    if "best player" in user_input_lower or "worst player" in user_input_lower:
        valid_players = [p for p in players if p.get("Player Points") is not None]
        if not valid_players:
            return "No players found with valid points data."
        
        best_player = max(valid_players, key=lambda p: p.get("Player Points", 0))
        worst_player = min(valid_players, key=lambda p: p.get("Player Points", 0))
        
        return (
            f"🏆 **Best Player:** {best_player['Name']} - {best_player['Player Points']} points\n"
            f"📉 **Worst Player:** {worst_player['Name']} - {worst_player['Player Points']} points"
        )
    
    # Fuzzy matching for categories
    best_match = get_best_match(user_input_lower, STANDARD_TERMS)
    
    if best_match in ["batsman", "bowler", "all-rounder"]:
        category_players = get_players_by_category(best_match)
        if not category_players:
            return f"❌ No {best_match}s found."
        
        response = [format_player_info(p, i+1) for i, p in enumerate(category_players)]
        return f"🏏 **{best_match.title()}s ({len(category_players)} found):**\n" + "\n".join(response)
    
    # If no match found, provide helpful suggestions
    return (
        "🤔 I didn't understand your query. Try asking about:\n"
        "• **'player list'** - to see all players\n"
        "• **'batsman'**, **'bowler'**, or **'all-rounder'** - to filter by category\n"
        "• **'best player'** - to see the best and worst players\n"
        "• **A number (1-{})** - to get details about a specific player".format(len(players))
    )

# Main UI
st.title("🏏 Player Chatbot")
st.markdown("---")

# Sidebar with instructions
with st.sidebar:
    st.header("📖 How to Use")
    st.markdown("""
    **Available Commands:**
    - `player list` - Show all players
    - `batsman` - Show all batsmen
    - `bowler` - Show all bowlers  
    - `all-rounder` - Show all all-rounders
    - `best player` - Show best & worst players
    - `[number]` - Get specific player details
    
    **Examples:**
    - "Show me all batsmen"
    - "Who is the best player?"
    - "3" (for 3rd player details)
    """)
    
    if players:
        st.markdown(f"**Total Players:** {len(players)}")
        categories = {}
        for p in players:
            cat = p.get('Category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        st.markdown("**By Category:**")
        for cat, count in categories.items():
            st.markdown(f"- {cat}: {count}")

# Main chat interface
col1, col2 = st.columns([3, 1])

with col1:
    user_input = st.text_input(
        "💬 Ask about players...", 
        placeholder="Try 'player list', 'batsman', 'best player', or a number...",
        key="user_input"
    )

with col2:
    clear_chat = st.button("🗑️ Clear", help="Clear the input")

if clear_chat:
    st.rerun()

# Process and display response
if user_input:
    with st.container():
        st.markdown("### 🤖 Bot Response:")
        response = process_query(user_input)
        
        # Display response in a nice box
        if response.startswith("❌"):
            st.error(response)
        elif response.startswith("🏆") or response.startswith("📋") or response.startswith("🏏"):
            st.success(response)
        else:
            st.info(response)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit • Ask about cricket players and their stats!*")

# Add some sample queries as buttons
st.markdown("### 🎯 Quick Actions:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📋 All Players"):
        st.session_state.user_input = "player list"
        st.rerun()

with col2:
    if st.button("🏏 Batsmen"):
        st.session_state.user_input = "batsman"
        st.rerun()

with col3:
    if st.button("⚡ Bowlers"):
        st.session_state.user_input = "bowler"
        st.rerun()

with col4:
    if st.button("🏆 Best Player"):
        st.session_state.user_input = "best player"
        st.rerun()