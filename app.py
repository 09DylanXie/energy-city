import streamlit as st
import copy
import pandas as pd

# --- THE 100% COMPLETE LOGIC ---
class EnergyCityAssistant:
    def __init__(self, name):
        self.name = name
        self.resources = {
            "Gold": 150, "Watts": 5, "Wood": 5, "Iron": 0, "Steel": 0, "Coal": 0,
            "Oil": 0, "Re-Oil": 0, "Uranium": 0, "Deuterium": 0, "Fission Cell": 0,
            "Fusion Cell": 0, "Dura-Steel": 0, "Fusion Core": 0,
            "Battery": 0, "Battery_Charge": 0
        }
        self.buildings = []
        self.utility_slots = []
        self.pending_watts = 0
        self.fusion_plants_built = 0
        self.shop_limits = {item: 0 for item in ["Wood", "Iron", "Coal", "Steel", "Oil", "Uranium", "Deuterium"]}
        self.turn_num = 1
        self.history = []
        # Added for the Charting feature
        self.stats_history = [{"Turn": 1, "Gold": 150, "Watts": 5}]

    def save_state(self):
        state = {
            "resources": copy.deepcopy(self.resources),
            "buildings": copy.deepcopy(self.buildings),
            "utility_slots": copy.deepcopy(self.utility_slots),
            "pending_watts": self.pending_watts,
            "fusion_plants_built": self.fusion_plants_built,
            "shop_limits": copy.deepcopy(self.shop_limits),
            "turn_num": self.turn_num
        }
        self.history.append(state)
        if len(self.history) > 10: self.history.pop(0)

    def undo(self):
        if not self.history: return "⚠️ Nothing to undo."
        state = self.history.pop()
        self.resources = state["resources"]
        self.buildings = state["buildings"]
        self.utility_slots = state["utility_slots"]
        self.pending_watts = state["pending_watts"]
        self.fusion_plants_built = state["fusion_plants_built"]
        self.shop_limits = state["shop_limits"]
        self.turn_num = state["turn_num"]
        # Remove the last stat entry if we undo a turn end
        if len(self.stats_history) > self.turn_num:
            self.stats_history.pop()
        return "↩️ Last action undone."

    # ... [Rest of your mechanical functions: shop_buy, build_plant, etc. remain the same] ...

# --- STREAMLIT UI ---
st.set_page_config(page_title="Energy City Assistant", layout="centered")

if 'game' not in st.session_state:
    st.session_state.game = EnergyCityAssistant("Tao")
    st.session_state.logs = []

game = st.session_state.game

# --- PREVIOUS TABS (Market, Build, Utility, Refine) GO HERE ---

# --- NEW STATS TAB ---
with st.expander("📈 Economy Stats"):
    if len(game.stats_history) > 1:
        df = pd.DataFrame(game.stats_history)
        st.line_chart(df.set_index("Turn"))
    else:
        st.info("End your first turn to start seeing economy trends!")

# --- UPDATED END TURN BUTTON ---
if st.button("⏭️ End Turn", use_container_width=True):
    game.save_state()
    game.turn_num += 1
    
    # Process turn mechanics
    game.resources["Watts"] += game.pending_watts
    game.pending_watts = 0
    for b in game.buildings: b['active'] = False
    
    mines = game.utility_slots.count("Gold Mine")
    game.resources["Gold"] += (mines * 30) + 20 # Allowance + Mines
    game.shop_limits = {item: 0 for item in ["Wood", "Iron", "Coal", "Steel", "Oil", "Uranium", "Deuterium"]}
    
    # Log stats for the chart
    game.stats_history.append({
        "Turn": game.turn_num, 
        "Gold": game.resources["Gold"], 
        "Watts": game.resources["Watts"]
    })
    st.rerun()