import streamlit as st
import copy
import pandas as pd

# --- THE COMPLETE LOGIC ---
class EnergyCityAssistant:
    def __init__(self, name):
        self.name = name
        self.resources = {
            "Gold": 150, "Watts": 5, "Wood": 5, "Iron": 0, "Steel": 0, "Coal": 0,
            "Oil": 0, "Re-Oil": 0, "Uranium": 0, "Deuterium": 0, "Fission Cell": 0,
            "Fusion Cell": 0, "Dura-Steel": 0, "Fusion Core": 0,
            "Battery": 0, "Battery_Charge": 0
        }
        self.buildings = [] # Max 6 [cite: 3]
        self.utility_slots = [] # Max 3 [cite: 3]
        self.pending_watts = 0
        self.fusion_plants_built = 0
        self.turn_num = 1
        self.battery_bought_turn = -1
        self.factory_used_this_turn = 0 # Max 6 per turn [cite: 19]
        self.history = []
        self.stats_history = [{"Turn": 1, "Gold": 150, "Watts": 5}]

    def save_state(self):
        state = {
            "resources": copy.deepcopy(self.resources),
            "buildings": copy.deepcopy(self.buildings),
            "utility_slots": copy.deepcopy(self.utility_slots),
            "pending_watts": self.pending_watts,
            "fusion_plants_built": self.fusion_plants_built,
            "turn_num": self.turn_num,
            "battery_bought_turn": self.battery_bought_turn,
            "factory_used_this_turn": self.factory_used_this_turn
        }
        self.history.append(state)

    def undo(self):
        if not self.history: return "⚠️ Nothing to undo."
        state = self.history.pop()
        self.resources = state["resources"]
        self.buildings = state["buildings"]
        self.utility_slots = state["utility_slots"]
        self.pending_watts = state["pending_watts"]
        self.fusion_plants_built = state["fusion_plants_built"]
        self.turn_num = state["turn_num"]
        self.battery_bought_turn = state["battery_bought_turn"]
        self.factory_used_this_turn = state["factory_used_this_turn"]
        if len(self.stats_history) > self.turn_num: self.stats_history.pop()
        return "↩️ Undone."

# --- APP INITIALIZATION ---
st.set_page_config(page_title="Energy City Assistant", layout="centered")

if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if not st.session_state.game_started:
    st.markdown("<h1 style='text-align: center;'>⚡ Welcome to Energy City!</h1>", unsafe_allow_html=True)
    player_name = st.text_input("Enter your name to begin:", placeholder="e.g. John")
    if st.button("Start Game", use_container_width=True):
        if player_name:
            st.session_state.game = EnergyCityAssistant(player_name)
            st.session_state.game_started = True
            st.rerun()
    st.stop()

game = st.session_state.game

# --- WIN CONDITION ---
if game.fusion_plants_built >= 2: # [cite: 2]
    st.balloons()
    st.markdown("<h1 style='text-align: center; color: gold;'>🏆 VICTORY!</h1>", unsafe_allow_html=True)
    if st.button("New Game", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.stop()

# --- SIDEBAR STATUS ---
st.sidebar.title(f"🏙️ {game.name.upper()}")
st.sidebar.header(f"Turn: {game.turn_num}")
st.sidebar.metric("💰 Gold", game.resources["Gold"])
st.sidebar.metric("⚡ Watts", game.resources["Watts"])
if game.resources["Battery"] > 0:
    st.sidebar.write(f"🔋 Battery: {game.resources['Battery_Charge']}/7W")
    st.sidebar.progress(game.resources["Battery_Charge"] / 7)
st.sidebar.write("---")
st.sidebar.subheader("📦 Inventory")
icons = {"Wood": "🪵", "Iron": "⛓️", "Steel": "🏗️", "Coal": "🪨", "Oil": "🛢️", "Re-Oil": "🧪", "Uranium": "☢️", "Deuterium": "💧", "Fission Cell": "🔋", "Fusion Cell": "⚛️", "Dura-Steel": "💎", "Fusion Core": "☀️"}
for res, val in game.resources.items():
    if val > 0 and res not in ["Gold", "Watts", "Battery", "Battery_Charge"]:
        st.sidebar.write(f"{icons.get(res, '📦')} **{res}:** {val}")

# --- ACTION TABS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛒 Market", "🏗️ Grid", "⚙️ Utility", "🧪 Refine", "🔋 Battery"])

with tab1:
    st.subheader("Marketplace")
    m_action = st.radio("Action", ["Buy", "Sell", "Trade"], horizontal=True)
    
    if m_action == "Buy":
        prices = {"Wood (20G)": ("Wood", 20), "Iron (20G)": ("Iron", 20), "Coal (40G)": ("Coal", 40), "Steel (70G)": ("Steel", 70), "Oil (50G)": ("Oil", 50), "Uranium (40G)": ("Uranium", 40), "Deuterium (90G)": ("Deuterium", 90), "Battery (10G)": ("Battery", 10)} # [cite: 36-39]
        choice = st.selectbox("Select Item", list(prices.keys()))
        item_name, item_price = prices[choice]
        qty = st.number_input("Quantity (Max 3/turn)", 1, 3, 1) # [cite: 35]
        cost = item_price * qty
        if st.button(f"Purchase {qty}x {item_name} ({cost}G)"):
            if item_name == "Battery" and game.resources["Battery"] > 0: st.error("Max 1 Battery.") # [cite: 41]
            elif game.resources["Gold"] >= cost:
                game.save_state(); game.resources["Gold"] -= cost; game.resources[item_name] += qty
                if item_name == "Battery": game.battery_bought_turn = game.turn_num
                st.rerun()
    elif m_action == "Sell":
        sell_opts = {"Steel (20G)": ("Steel", 20, "Gold"), "Re-Oil (20G)": ("Re-Oil", 20, "Gold"), "Fission Cell (20G)": ("Fission Cell", 20, "Gold"), "Fusion Cell (20G)": ("Fusion Cell", 20, "Gold"), "Wood (1W)": ("Wood", 1, "Watts"), "Iron (1W)": ("Iron", 1, "Watts"), "Coal (1W)": ("Coal", 1, "Watts"), "Oil (1W)": ("Oil", 1, "Watts")} # [cite: 16, 17]
        s_choice = st.selectbox("Select Item to Sell", list(sell_opts.keys()))
        s_name, s_val, s_type = sell_opts[s_choice]
        if st.button(f"Sell 1 unit of {s_name}"):
            if game.resources[s_name] >= 1:
                game.save_state()
                if s_type == "Gold": game.resources["Gold"] += s_val
                else: game.resources["Watts"] += s_val
                game.resources[s_name] -= 1; st.rerun()
    else:
        st.subheader("🤝 Player Trade")
        trade_items = ["Gold", "Wood", "Iron", "Coal", "Steel", "Oil", "Re-Oil", "Uranium", "Deuterium", "Fission Cell", "Fusion Cell", "Dura-Steel", "Fusion Core"]
        col1, col2 = st.columns(2)
        
        give_res = col1.selectbox("Give away:", trade_items)
        give_qty = col1.number_input("Qty to Give:", 0, 1000, 0)
        
        receive_res = col2.selectbox("Receive from player:", trade_items)
        receive_qty = col2.number_input("Qty to Receive:", 0, 1000, 0)
        
        if st.button("Execute Trade"):
            if game.resources.get(give_res, 0) >= give_qty:
                game.save_state()
                game.resources[give_res] -= give_qty
                game.resources[receive_res] += receive_qty
                st.success(f"Traded {give_qty} {give_res} for {receive_qty} {receive_res}!")
                st.rerun()
            else:
                st.error(f"You don't have enough {give_res}!")

with tab2:
    st.subheader("Power Grid")
    st.write(f"Used Slots: {len(game.buildings)} / 6") # [cite: 3]
    st.progress(len(game.buildings)/6)
    
    plants = {"Bio (20G + 3 Wood)": ("Bio", 20, "Wood", 3), "Coal (30G + 3 Coal)": ("Coal", 30, "Coal", 3), "Oil (50G + 3 Re-Oil)": ("Oil", 50, "Re-Oil", 3), "Fission (100G + 3 Fission Cell)": ("Fission", 100, "Fission Cell", 3), "Fusion (150G + 1 Fusion Core)": ("Fusion", 150, "Fusion Core", 1)} # [cite: 9, 10]
    p_choice = st.selectbox("Build New Plant", list(plants.keys()))
    p_type, p_gold, p_mat, p_amt = plants[p_choice]
    
    if st.button("Construct Plant"):
        if len(game.buildings) < 6 and game.resources["Gold"] >= p_gold and game.resources.get(p_mat, 0) >= p_amt:
            game.save_state(); game.resources["Gold"] -= p_gold; game.resources[p_mat] -= p_amt
            game.buildings.append({'type': p_type, 'active': False}); st.rerun()
    
    st.divider()
    pwr_data = {"Bio": {"cost": 1, "prod": 2}, "Coal": {"cost": 2, "prod": 4}, "Oil": {"cost": 3, "prod": 7}, "Fission": {"cost": 4, "prod": 10}, "Fusion": {"cost": 5, "prod": 15}} # [cite: 13]
    
    for i, b in enumerate(game.buildings):
        c1, c2, c3 = st.columns([2, 1, 1])
        stats = pwr_data[b['type']]
        icon = "🟢" if b['active'] else "⚪"
        c1.write(f"{icon} **{b['type']}** (⚡-{stats['cost']}W | ⚡+{stats['prod']}W)")
        if not b['active'] and c2.button(f"Power", key=f"pwr_{i}"):
            if game.resources["Watts"] >= stats['cost']:
                game.save_state(); game.resources["Watts"] -= stats['cost']; b['active'] = True
                game.pending_watts += stats['prod']; st.rerun()
        if c3.button("🗑️", key=f"del_b_{i}"):
            refund = {"Bio": 20, "Coal": 30, "Oil": 50, "Fission": 100, "Fusion": 150} # [cite: 11]
            game.save_state(); game.resources["Gold"] += refund[b['type']]
            game.buildings.pop(i); st.rerun()

with tab3:
    st.subheader("Utility Management")
    st.write(f"Used Slots: {len(game.utility_slots)} / 3") # [cite: 3]
    st.progress(len(game.utility_slots)/3)
    
    u_opts = {"Factory (10G+1Wd)": "Factory", "Refinery (20G+1Ir)": "Refinery", "Mine (60G+1St)": "Mine"} # [cite: 9]
    u_choice = st.selectbox("Build Utility", list(u_opts.keys()))
    if st.button("Construct"):
        costs = {"Factory": (10, "Wood", 1), "Refinery": (20, "Iron", 1), "Mine": (60, "Steel", 1)}
        u_gold, u_mat, u_amt = costs[u_opts[u_choice]]
        if len(game.utility_slots) < 3 and game.resources["Gold"] >= u_gold and game.resources[u_mat] >= u_amt:
            game.save_state(); game.resources["Gold"] -= u_gold; game.resources[u_mat] -= u_amt
            game.utility_slots.append(u_opts[u_choice]); st.rerun()

    if "Factory" in game.utility_slots:
        st.divider(); st.subheader("🏭 Factory Production")
        rem_factory = 6 - game.factory_used_this_turn # [cite: 19]
        if rem_factory > 0:
            f_res = st.selectbox("Resource", ["Wood", "Iron", "Coal", "Oil", "Uranium"])
            f_amt = st.slider("Units", 1, rem_factory, 1)
            if st.button(f"Produce {f_amt} {f_res} (Cost: {f_amt}W)"): # [cite: 20]
                if game.resources["Watts"] >= f_amt:
                    game.save_state(); game.resources["Watts"] -= f_amt; game.resources[f_res] += f_amt
                    game.factory_used_this_turn += f_amt; st.rerun()
        else: st.warning("Factory limit reached!")

with tab4:
    st.subheader("🧪 Refinement")
    if "Refinery" in game.utility_slots:
        # [cite: 22, 24-34]
        ref_rules = {
            "Steel (1 Iron + 2W)": ("Steel", {"Iron": 1}, 2),
            "Dura-Steel (1 Steel + 5W)": ("Dura-Steel", {"Steel": 1}, 5),
            "Re-Oil (2 Oil + 1W)": ("Re-Oil", {"Oil": 2}, 1),
            "Deuterium (3 Uranium + 1W)": ("Deuterium", {"Uranium": 3}, 1),
            "Fission Cell (2 Uranium + 2W)": ("Fission Cell", {"Uranium": 2}, 2),
            "Fusion Cell (2 Deuterium + 3W)": ("Fusion Cell", {"Deuterium": 2}, 3),
            "Fusion Core (3 Dura-Steel + 3 Fusion Cell + 50G + 18W)": ("Fusion Core", {"Dura-Steel": 3, "Fusion Cell": 3, "Gold": 50}, 18)
        }
        r_choice = st.selectbox("Select Refinement", list(ref_rules.keys()))
        target, mats, r_watts = ref_rules[r_choice]
        if st.button("Begin Refinement"):
            can_afford = all(game.resources.get(m, 0) >= a for m, a in mats.items()) and game.resources["Watts"] >= r_watts
            if can_afford:
                game.save_state()
                for m, a in mats.items(): game.resources[m] -= a
                game.resources["Watts"] -= r_watts; game.resources[target] += 1; st.rerun()
            else: st.error("Missing components!")

with tab5:
    st.subheader("🔋 Battery")
    if game.resources["Battery"] > 0:
        max_c = min(game.resources["Watts"], 7 - game.resources["Battery_Charge"]) # [cite: 41]
        if max_c > 0:
            c_amt = st.slider("Charge Watts", 0, max_c, 0)
            if st.button("Move to Battery"):
                game.save_state(); game.resources["Watts"] -= c_amt; game.resources["Battery_Charge"] += c_amt; st.rerun()
        
        if st.button("Sell Battery") and game.turn_num > game.battery_bought_turn: # [cite: 42]
            resale = 10 + (10 * game.resources["Battery_Charge"]) # [cite: 41]
            game.save_state(); game.resources["Gold"] += resale
            game.resources["Battery"] = 0; game.resources["Battery_Charge"] = 0; st.rerun()

# --- FOOTER ---
st.divider()
c1, c2, c3 = st.columns(3)
if c1.button("↩️ Undo", use_container_width=True):
    game.undo(); st.rerun()
if c2.button("⏭️ End Turn", use_container_width=True):
    game.save_state()
    game.turn_num += 1
    game.resources["Watts"] += game.pending_watts; game.pending_watts = 0 # [cite: 13]
    for b in game.buildings: b['active'] = False
    game.resources["Gold"] += (game.utility_slots.count("Mine") * 30) + 20 # [cite: 6, 21]
    game.factory_used_this_turn = 0
    st.rerun()
if c3.button("🗑️ Reset", use_container_width=True):
    st.session_state.clear(); st.rerun()