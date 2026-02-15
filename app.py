import streamlit as st
import copy
import pandas as pd
import random

# --- THE COMPLETE LOGIC ---
class EnergyCityAssistant:
    def __init__(self, name):
        self.name = name
        self.resources = {
            "Gold": 150, "Watts": 7, "Wood": 7, "Iron": 0, "Steel": 0, "Coal": 0,
            "Oil": 0, "Re-Oil": 0, "Uranium": 0, "Deuterium": 0, "Fission Cell": 0,
            "Fusion Cell": 0, "Dura-Steel": 0, "Fusion Core": 0,
            "Battery": 0, "Battery_Charge": 0
        }
        self.buildings = [] 
        self.utility_slots = [] 
        self.pending_watts = 0
        self.fusion_plants_built = 0
        self.turn_num = 1
        self.battery_bought_turn = -1
        self.factory_used_this_turn = 0 
        self.bank_deposits = []
        self.history = []
        self.stats_history = [{"Turn": 1, "Gold": 150, "Watts": 7}]

    def save_state(self):
        state = {
            "resources": copy.deepcopy(self.resources),
            "buildings": copy.deepcopy(self.buildings),
            "utility_slots": copy.deepcopy(self.utility_slots),
            "pending_watts": self.pending_watts,
            "fusion_plants_built": self.fusion_plants_built,
            "turn_num": self.turn_num,
            "battery_bought_turn": self.battery_bought_turn,
            "factory_used_this_turn": self.factory_used_this_turn,
            "bank_deposits": copy.deepcopy(self.bank_deposits)
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
        self.bank_deposits = state["bank_deposits"]
        if len(self.stats_history) > self.turn_num: self.stats_history.pop()
        return "↩️ Undone."

# --- APP INITIALIZATION ---
st.set_page_config(page_title="Energy City Assistant", layout="centered")

if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if not st.session_state.game_started:
    st.markdown("<h1 style='text-align: center;'>⚡ Welcome to Energy City!</h1>", unsafe_allow_html=True)
    player_name = st.text_input("Enter your name to begin:", placeholder="e.g. Dylan")
    if st.button("Start Game", use_container_width=True):
        if player_name:
            st.session_state.game = EnergyCityAssistant(player_name)
            st.session_state.game_started = True
            st.session_state.logs.append(f"Game started for {player_name}")
            st.rerun()
    st.stop()

game = st.session_state.game

# --- WIN CONDITION ---
if game.fusion_plants_built >= 2:
    st.balloons()
    st.markdown("<h1 style='text-align: center; color: gold;'>🏆 VICTORY!</h1>", unsafe_allow_html=True)
    if st.button("New Game", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    st.stop()

# --- SIDEBAR STATUS ---
st.sidebar.title(f"🏙️ {game.name.upper()}")
st.sidebar.header(f"Turn: {game.turn_num}")
st.sidebar.subheader("🏆 Victory Progress")
st.sidebar.write(f"Fusion Plants: {game.fusion_plants_built} / 2")
st.sidebar.progress(game.fusion_plants_built / 2)
st.sidebar.divider()
st.sidebar.metric("💰 Gold", game.resources["Gold"])
st.sidebar.metric("⚡ Watts", game.resources["Watts"])
if game.resources["Battery"] > 0:
    st.sidebar.write(f"🔋 Battery: {game.resources['Battery_Charge']}/7W")
    st.sidebar.progress(game.resources["Battery_Charge"] / 7.0)
st.sidebar.write("---")
st.sidebar.subheader("📦 Inventory")
icons = {"Wood": "🪵", "Iron": "⛓️", "Steel": "🏗️", "Coal": "🪨", "Oil": "🛢️", "Re-Oil": "🧪", "Uranium": "☢️", "Deuterium": "💧", "Fission Cell": "🔋", "Fusion Cell": "⚛️", "Dura-Steel": "💎", "Fusion Core": "☀️"}
for res, val in game.resources.items():
    if val > 0 and res not in ["Gold", "Watts", "Battery", "Battery_Charge"]:
        st.sidebar.write(f"{icons.get(res, '📦')} **{res}:** {val}")

# --- ACTION TABS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🛒 Market", "🏗️ Grid", "⚙️ Utility", "🧪 Refine", "🔋 Battery", "🏦 Bank", "📜 History"])

with tab1:
    m_action = st.radio("Action", ["Buy", "Sell", "Trade", "Converter"], horizontal=True)
    if m_action == "Buy":
        prices = {"Wood (20G)": ("Wood", 20), "Iron (20G)": ("Iron", 20), "Coal (40G)": ("Coal", 40), "Steel (70G)": ("Steel", 70), "Oil (50G)": ("Oil", 50), "Uranium (40G)": ("Uranium", 40), "Deuterium (90G)": ("Deuterium", 90), "Battery (10G)": ("Battery", 10)}
        choice = st.selectbox("Select Item", list(prices.keys()))
        item_name, item_price = prices[choice]
        qty = st.number_input("Quantity", 1, 3, 1)
        cost = item_price * qty
        if st.button(f"Purchase {qty}x {item_name} ({cost}G)"):
            if item_name == "Battery" and game.resources["Battery"] > 0: st.error("Max 1 Battery.")
            elif game.resources["Gold"] >= cost:
                game.save_state(); game.resources["Gold"] -= cost; game.resources[item_name] += qty
                if item_name == "Battery": 
                    game.battery_bought_turn = game.turn_num
                    game.resources["Battery_Charge"] = 0
                st.session_state.logs.insert(0, f"Turn {game.turn_num}: Bought {qty} {item_name}")
                st.rerun()
    elif m_action == "Sell":
        sell_opts = {"Steel (20G)": ("Steel", 20, "Gold"), "Re-Oil (20G)": ("Re-Oil", 20, "Gold"), "Fission Cell (20G)": ("Fission Cell", 20, "Gold"), "Fusion Cell (20G)": ("Fusion Cell", 20, "Gold"), "Wood (1W)": ("Wood", 1, "Watts"), "Iron (1W)": ("Iron", 1, "Watts"), "Coal (1W)": ("Coal", 1, "Watts"), "Oil (1W)": ("Oil", 1, "Watts")}
        s_choice = st.selectbox("Select Item to Sell", list(sell_opts.keys()))
        s_name, s_val, s_type = sell_opts[s_choice]
        if st.button(f"Sell 1 unit of {s_name}"):
            if game.resources[s_name] >= 1:
                game.save_state()
                if s_type == "Gold": game.resources["Gold"] += s_val
                else: game.resources["Watts"] += s_val
                game.resources[s_name] -= 1; st.rerun()
    elif m_action == "Trade":
        st.subheader("🤝 Player Trade")
        trade_items = ["Gold", "Wood", "Iron", "Coal", "Steel", "Oil", "Re-Oil", "Uranium", "Deuterium", "Fission Cell", "Fusion Cell", "Dura-Steel", "Fusion Core"]
        col1, col2 = st.columns(2)
        give_res = col1.selectbox("Give:", trade_items); give_qty = col1.number_input("Qty Give:", 0, 1000, 0)
        receive_res = col2.selectbox("Receive:", trade_items); receive_qty = col2.number_input("Qty Rec:", 0, 1000, 0)
        if st.button("Execute Trade"):
            if game.resources.get(give_res, 0) >= give_qty:
                game.save_state(); game.resources[give_res] -= give_qty; game.resources[receive_res] += receive_qty
                st.session_state.logs.insert(0, f"Turn {game.turn_num}: Traded {give_qty} {give_res} for {receive_qty} {receive_res}"); st.rerun()
    else:
        st.subheader("🔌 Watt Converter")
        conv_mode = st.radio("Exchange Type", ["Gold to Watts (20G → 1W)", "Watts to Gold (1W → 10G)"])
        if conv_mode == "Gold to Watts (20G → 1W)":
            max_w = game.resources["Gold"] // 20
            w_to_buy = st.number_input("Watts to Buy:", 0, max_w, 0)
            if st.button(f"Convert {w_to_buy * 20} Gold into {w_to_buy} Watts"):
                if w_to_buy > 0:
                    game.save_state(); game.resources["Gold"] -= (w_to_buy * 20); game.resources["Watts"] += w_to_buy
                    st.rerun()
        else:
            max_g_conv = game.resources["Watts"]
            w_to_sell = st.number_input("Watts to Sell:", 0, max_g_conv, 0)
            if st.button(f"Convert {w_to_sell} Watts into {w_to_sell * 10} Gold"):
                if w_to_sell > 0:
                    game.save_state(); game.resources["Watts"] -= w_to_sell; game.resources["Gold"] += (w_to_sell * 10)
                    st.rerun()

with tab2:
    st.write(f"Used Slots: {len(game.buildings)} / 6")
    st.progress(len(game.buildings)/6.0)
    
    plants = {
        "Bio (20G+3Wd)": {"type": "Bio", "gold": 20, "mat": "Wood", "amt": 3, "req": None},
        "Coal (30G+3Cl)": {"type": "Coal", "gold": 30, "mat": "Coal", "amt": 3, "req": "Bio"},
        "Oil (50G+3Re)": {"type": "Oil", "gold": 50, "mat": "Re-Oil", "amt": 3, "req": "Coal"},
        "Fission (100G+5Fi)": {"type": "Fission", "gold": 100, "mat": "Fission Cell", "amt": 5, "req": "Oil"}, # Updated to 5 Cells
        "Fusion (150G+1Core)": {"type": "Fusion", "gold": 150, "mat": "Fusion Core", "amt": 1, "req": "Fission"}
    }
    
    p_choice = st.selectbox("Construct/Upgrade Plant", list(plants.keys()))
    p_data = plants[p_choice]
    if st.button("Confirm Construction"):
        if len(game.buildings) >= 6 and p_data["req"] is None: st.error("❌ Grid full.")
        elif p_data["req"] and not any(b['type'] == p_data["req"] for b in game.buildings): st.error(f"❌ Need a {p_data['req']} Plant.")
        elif game.resources["Gold"] >= p_data["gold"] and game.resources.get(p_data["mat"], 0) >= p_data["amt"]:
            game.save_state()
            if p_data["req"]:
                idx = next(i for i, b in enumerate(game.buildings) if b['type'] == p_data["req"])
                game.buildings.pop(idx)
            game.resources["Gold"] -= p_data["gold"]; game.resources[p_data["mat"]] -= p_data["amt"]
            game.buildings.append({'type': p_data["type"], 'active': False})
            if p_data["type"] == "Fusion": game.fusion_plants_built += 1
            st.rerun()
        else: st.error("❌ Not enough Gold or Materials.")

    st.divider()
    pwr_data = {"Bio": (1, 3), "Coal": (2, 6), "Oil": (3, 8), "Fission": (4, 14), "Fusion": (5, 20)}
    for i, b in enumerate(game.buildings):
        c1, c2, c3 = st.columns([2, 1, 1])
        c_pwr, p_pwr = pwr_data[b['type']]
        c1.write(f"{'🟢' if b['active'] else '⚪'} **{b['type']}** (⚡-{c_pwr} | ⚡+{p_pwr})")
        if not b['active'] and c2.button("Power", key=f"pwr_{i}"):
            if game.resources["Watts"] >= c_pwr:
                game.save_state(); game.resources["Watts"] -= c_pwr; b['active'] = True
                game.pending_watts += p_pwr; st.rerun()
        if c3.button("🗑️", key=f"del_b_{i}"):
            if b['type'] == "Fusion": game.fusion_plants_built -= 1
            refund = {"Bio": 20, "Coal": 30, "Oil": 50, "Fission": 100, "Fusion": 150}
            game.save_state(); game.resources["Gold"] += refund[b['type']]; game.buildings.pop(i); st.rerun()

with tab3:
    st.write(f"Used Slots: {len(game.utility_slots)} / 3")
    st.progress(len(game.utility_slots)/3.0)
    u_opts = {"Factory (10G+1Wd)": "Factory", "Refinery (40G+1Ir)": "Refinery", "Mine (40G+1St)": "Mine"}
    u_choice = st.selectbox("Construct Utility", list(u_opts.keys()))
    if st.button("Build Utility"):
        costs = {"Factory": (10, "Wood", 1), "Refinery": (40, "Iron", 1), "Mine": (40, "Steel", 1)}
        u_gold, u_mat, u_amt = costs[u_opts[u_choice]]
        if len(game.utility_slots) < 3 and game.resources["Gold"] >= u_gold and game.resources[u_mat] >= u_amt:
            game.save_state(); game.resources["Gold"] -= u_gold; game.resources[u_mat] -= u_amt
            game.utility_slots.append(u_opts[u_choice]); st.rerun()

    if "Mine" in game.utility_slots:
        st.divider(); st.subheader("💎 Mega-Mine Upgrade")
        st.write("Description: Increases passive income to 60 Gold per turn.")
        if st.button("Upgrade to Mega-Mine (70G + 1 Dura-Steel)"):
            if game.resources["Gold"] >= 70 and game.resources["Dura-Steel"] >= 1:
                game.save_state(); game.resources["Gold"] -= 70; game.resources["Dura-Steel"] -= 1
                idx = game.utility_slots.index("Mine"); game.utility_slots[idx] = "Mega-Mine"; st.rerun()

    if "Factory" in game.utility_slots:
        st.divider(); st.subheader("⚙️ Mega-Factory Upgrade")
        st.write("Description: Doubled capacity (10 units per turn).")
        if st.button("Upgrade to Mega-Factory (100G + 2 Dura-Steel)"):
            if game.resources["Gold"] >= 100 and game.resources["Dura-Steel"] >= 2:
                game.save_state(); game.resources["Gold"] -= 100; game.resources["Dura-Steel"] -= 2
                idx = game.utility_slots.index("Factory"); game.utility_slots[idx] = "Mega-Factory"; st.rerun()

    if "Refinery" in game.utility_slots:
        st.divider(); st.subheader("🧪 Mega-Refinery Upgrade")
        st.write("Description: Efficiency bonus (-1 Watt per refinement).")
        if st.button("Upgrade to Mega-Refinery (50G + 1 Dura-Steel)"):
            if game.resources["Gold"] >= 50 and game.resources["Dura-Steel"] >= 1:
                game.save_state(); game.resources["Gold"] -= 50; game.resources["Dura-Steel"] -= 1
                idx = game.utility_slots.index("Refinery"); game.utility_slots[idx] = "Mega-Refinery"; st.rerun()

    if any(f in game.utility_slots for f in ["Factory", "Mega-Factory"]):
        st.divider(); st.subheader("🏭 Factory Production")
        is_mega = "Mega-Factory" in game.utility_slots
        limit = 10 if is_mega else 5
        rem = limit - game.factory_used_this_turn
        if rem > 0:
            f_res = st.selectbox("Resource", ["Wood", "Iron", "Coal", "Oil", "Uranium"])
            if rem > 1: f_amt = st.slider("Units", 1, rem, 1)
            else: f_amt = 1; st.info("1 unit capacity remains.")
            if st.button(f"Produce {f_amt} {f_res} (Cost: {f_amt}W)"):
                if game.resources["Watts"] >= f_amt:
                    game.save_state(); game.resources["Watts"] -= f_amt; game.resources[f_res] += f_amt
                    game.factory_used_this_turn += f_amt; st.rerun()

    st.write("---")
    for i, u in enumerate(game.utility_slots):
        c1, c2 = st.columns([3, 1])
        c1.write(f"- {u}")
        if c2.button("🗑️", key=f"del_u_{i}"): game.save_state(); game.utility_slots.pop(i); st.rerun()

with tab4:
    if any(r in game.utility_slots for r in ["Refinery", "Mega-Refinery"]):
        st.subheader("🧪 Refinement")
        is_mega = "Mega-Refinery" in game.utility_slots
        w_mod = 1 if is_mega else 0
        ref_rules = {
            f"Steel (1 Iron + {2-w_mod}W)": ("Steel", {"Iron": 1}, 2-w_mod),
            f"Dura-Steel (1 Steel + {5-w_mod}W)": ("Dura-Steel", {"Steel": 1}, 5-w_mod),
            f"Re-Oil (2 Oil + {max(0, 1-w_mod)}W)": ("Re-Oil", {"Oil": 2}, max(0, 1-w_mod)),
            f"Deuterium (3 Uranium + {max(0, 1-w_mod)}W)": ("Deuterium", {"Uranium": 3}, max(0, 1-w_mod)),
            f"Fission Cell (2 Uranium + {8-w_mod}W)": ("Fission Cell", {"Uranium": 2}, 8-w_mod), # Updated to 8 Watts
            f"Fusion Cell (2 Deuterium + {3-w_mod}W)": ("Fusion Cell", {"Deuterium": 2}, 3-w_mod),
            f"Fusion Core (3 Dura+3Cell+{18-w_mod}W+50G)": ("Fusion Core", {"Dura-Steel": 3, "Fusion Cell": 3, "Gold": 50}, 18-w_mod)
        }
        r_choice = st.selectbox("Select Refinement", list(ref_rules.keys()))
        target, mats, r_watts = ref_rules[r_choice]
        if st.button("Refine"):
            if all(game.resources.get(m, 0) >= a for m, a in mats.items()) and game.resources["Watts"] >= r_watts:
                game.save_state()
                for m, a in mats.items(): game.resources[m] -= a
                game.resources["Watts"] -= r_watts; game.resources[target] += 1; st.rerun()
    else: st.info("Need a Refinery utility.")

with tab5:
    if game.resources["Battery"] > 0:
        max_c = min(game.resources["Watts"], 7 - game.resources["Battery_Charge"])
        if max_c > 1:
            c_amt = st.slider("Charge Watts", 0, max_c, 0)
            if st.button("Store Energy"):
                game.save_state(); game.resources["Watts"] -= c_amt; game.resources["Battery_Charge"] += c_amt; st.rerun()
        elif max_c == 1:
            if st.button("Store 1 Watt"):
                game.save_state(); game.resources["Watts"] -= 1; game.resources["Battery_Charge"] += 1; st.rerun()
        if st.button("Sell Battery") and game.turn_num > game.battery_bought_turn:
            resale = 10 + (15 * game.resources["Battery_Charge"])
            game.save_state(); game.resources["Gold"] += resale; game.resources["Battery"] = 0; st.rerun()
    else: st.info("Buy a Battery in Market.")

with tab6:
    st.subheader("🏦 The Bank")
    b_col1, b_col2 = st.columns(2); b_type = b_col1.selectbox("Asset Type", ["Gold", "Watts"])
    b_amt = b_col2.number_input(f"Amount", 0, game.resources[b_type], 0)
    if st.button(f"Deposit {b_amt} {b_type}"):
        if b_amt > 0:
            game.save_state(); game.resources[b_type] -= b_amt
            game.bank_deposits.append({"type": b_type, "amount": b_amt, "return_turn": game.turn_num + 2})
            st.rerun()
    st.divider()
    for d in game.bank_deposits:
        rem = d['return_turn'] - game.turn_num
        st.write(f"- **{d['amount']} {d['type']}** (Turn {d['return_turn']} | {rem} left)")

with tab7:
    st.subheader("Turn History")
    df = pd.DataFrame(game.stats_history)
    st.line_chart(df.set_index("Turn"))
    for log in st.session_state.logs[:15]: st.write(f"- {log}")

# --- FOOTER ---
st.divider()
c1, c2, c3 = st.columns(3)
if c1.button("↩️ Undo", use_container_width=True): game.undo(); st.rerun()
if c2.button("⏭️ End Turn", use_container_width=True):
    game.save_state()
    if random.random() < 0.2:
        dtype = random.choice(["Gold", "Watts"])
        if dtype == "Gold":
            loss = random.randint(10, 30); game.resources["Gold"] = max(0, game.resources["Gold"] - loss)
            st.toast(f"🌪️ Disaster! Lost {loss} Gold.")
        else:
            loss = random.randint(2, 5); game.pending_watts = max(0, game.pending_watts - loss)
            st.toast(f"🌪️ Disaster! Lost {loss} Watts.")
    game.turn_num += 1
    matured = [d for d in game.bank_deposits if d['return_turn'] == game.turn_num]
    game.bank_deposits = [d for d in game.bank_deposits if d['return_turn'] != game.turn_num]
    for d in matured:
        payout = int(d['amount'] * 1.3); game.resources[d['type']] += payout
        st.toast(f"🏦 Bank Payout: {payout} {d['type']}")
    game.resources["Watts"] += game.pending_watts; game.pending_watts = 0
    for b in game.buildings: b['active'] = False
    m, mm = game.utility_slots.count("Mine"), game.utility_slots.count("Mega-Mine")
    game.resources["Gold"] += (m * 30) + (mm * 60) + 20
    game.factory_used_this_turn = 0; game.stats_history.append({"Turn": game.turn_num, "Gold": game.resources["Gold"], "Watts": game.resources["Watts"]})
    st.rerun()
if c3.button("🗑️ Reset", use_container_width=True): st.session_state.clear(); st.rerun()