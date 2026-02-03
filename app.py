import streamlit as st
import copy

# --- THE GAME LOGIC ---
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
        self.turn_num = 1
        self.history = []

    def save_state(self):
        state = {
            "resources": copy.deepcopy(self.resources),
            "buildings": copy.deepcopy(self.buildings),
            "utility_slots": copy.deepcopy(self.utility_slots),
            "pending_watts": self.pending_watts,
            "fusion_plants_built": self.fusion_plants_built,
            "turn_num": self.turn_num
        }
        self.history.append(state)

    def undo(self):
        if not self.history: return False
        state = self.history.pop()
        self.resources = state["resources"]
        self.buildings = state["buildings"]
        self.utility_slots = state["utility_slots"]
        self.pending_watts = state["pending_watts"]
        self.fusion_plants_built = state["fusion_plants_built"]
        self.turn_num = state["turn_num"]
        return True

    def build_plant(self, p_type):
        plants = {
            "Bio": {"Gold": 20, "Mat": "Wood", "Amt": 3},
            "Coal": {"Gold": 30, "Req": "Bio", "Mat": "Coal", "Amt": 3},
            "Oil": {"Gold": 50, "Req": "Coal", "Mat": "Re-Oil", "Amt": 3},
            "Fission": {"Gold": 100, "Req": "Oil", "Mat": "Fission Cell", "Amt": 3},
            "Fusion": {"Gold": 150, "Req": "Fission", "Mat": "Fusion Core", "Amt": 1}
        }
        p = plants.get(p_type)
        
        # Win Condition Logic: Fusion Plants
        if self.resources["Gold"] >= p["Gold"] and self.resources.get(p["Mat"], 0) >= p["Amt"]:
            self.resources["Gold"] -= p["Gold"]
            self.resources[p["Mat"]] -= p["Amt"]
            self.buildings.append({'type': p_type, 'active': False})
            if p_type == "Fusion":
                self.fusion_plants_built += 1
            return f"🏗️ Built {p_type} Plant!"
        return "❌ Missing Materials or Gold."

# --- STREAMLIT UI ---
st.set_page_config(page_title="Energy City", layout="centered")

if 'game' not in st.session_state:
    st.session_state.game = EnergyCityAssistant("Player 1")
    st.session_state.logs = ["Welcome to Energy City!"]

game = st.session_state.game

# --- WIN SCREEN CHECK ---
if game.fusion_plants_built >= 2:
    st.balloons()
    st.title("🏆 VICTORY!")
    st.header(f"Congratulations, {game.name}!")
    st.write(f"You have successfully built 2 Fusion Plants and solved the energy crisis in **{game.turn_num} turns**.")
    
    if st.button("Play Again", type="primary"):
        st.session_state.clear()
        st.rerun()
    st.stop() # Stops the rest of the app from rendering

# --- REGULAR GAME UI ---
st.sidebar.title(f"🏙️ {game.name}")
st.sidebar.metric("💰 Gold", f"${game.resources['Gold']}")
st.sidebar.metric("⚡ Watts", game.resources["Watts"])
st.sidebar.write(f"⚛️ Fusion Plants: {game.fusion_plants_built}/2")

# Sidebar Progress Bar
st.sidebar.progress(game.fusion_plants_built / 2)

# Main Interaction Tabs
tab1, tab2, tab3 = st.tabs(["🛒 Market", "🏗️ Build", "🔋 Battery"])

with tab2:
    st.subheader("Expand the Grid")
    plant_choice = st.selectbox("Select Plant", ["Bio", "Coal", "Oil", "Fission", "Fusion"])
    if st.button("Construct Building"):
        game.save_state()
        msg = game.build_plant(plant_choice)
        st.session_state.logs.insert(0, msg)
        st.rerun()

# [Include previous tab3/tab4 logic here for Market and Battery...]

# Footer Buttons
st.divider()
c1, c2, c3 = st.columns(3)
if c1.button("↩️ Undo"):
    if game.undo(): st.rerun()
if c2.button("⏭️ End Turn"):
    game.save_state()
    game.turn_num += 1
    game.resources["Gold"] += 20
    st.rerun()
if c3.button("🗑️ Reset"):
    st.session_state.clear()
    st.rerun()

st.caption("Log")
for log in st.session_state.logs[:3]:
    st.write(f"• {log}")