# import streamlit as st
# import pandas as pd

# # 🎯 Title
# st.title("🎯 Real-Time Color Predictor Strategy Tester")

# # 👉 Sidebar User Inputs
# wallet_input = st.sidebar.number_input("💰 Starting Wallet (₹):", min_value=1, value=1000)
# initial_bet_input = st.sidebar.number_input("🎯 Starting Bet (₹):", min_value=0.5, value=1.0, step=0.5)
# win_stop = st.sidebar.number_input("✅ Stop After How Many Wins?", min_value=1, value=4)
# multiplier = 2.25
# return_ratio = 1.98

# # 📦 Initialize Session State
# if "history" not in st.session_state:
#     st.session_state.history = []
# if "wallet" not in st.session_state:
#     st.session_state.wallet = wallet_input
# if "bet" not in st.session_state:
#     st.session_state.bet = initial_bet_input
# if "wins" not in st.session_state:
#     st.session_state.wins = 0
# if "total_loss" not in st.session_state:
#     st.session_state.total_loss = 0.0
# if "round" not in st.session_state:
#     st.session_state.round = 1
# if "active" not in st.session_state:
#     st.session_state.active = True

# # 👉 Info
# st.markdown("⏱️ You have 30 seconds to place each bet before entering the outcome.")
# st.markdown("🔁 After each round, input the result and system will auto-calculate everything.")

# # ▶️ Active Betting
# if st.session_state.active:
#     st.subheader(f"🎲 Round {st.session_state.round}")
#     st.write(f"💼 Wallet: ₹{st.session_state.wallet:.2f}")
#     st.write(f"🎯 Current Bet: ₹{st.session_state.bet:.2f}")

#     your_color = st.radio("🎨 Choose your color to bet on:", ["Red", "Green"], key=st.session_state.round)
#     actual_color = st.selectbox("🎲 Enter the RESULT color:", ["Red", "Green"], key=f"result_{st.session_state.round}")

#     if st.button("✅ Submit Round Result"):
#         bet = st.session_state.bet
#         wallet = st.session_state.wallet
#         wallet -= bet
#         st.session_state.total_loss += bet

#         win = (your_color == actual_color)
#         win_return = round(bet * return_ratio, 2) if win else 0.0
#         wallet += win_return
#         net_pnl = round(wallet - wallet_input, 2)
#         won = "✅" if win else "❌"

#         st.session_state.wallet = wallet

#         # Track data
#         st.session_state.history.append({
#             "Round": st.session_state.round,
#             "Bet ₹": round(bet, 2),
#             "Total Loss ₹": round(st.session_state.total_loss, 2),
#             "Win Return ₹": win_return,
#             "Net PnL ₹": net_pnl,
#             "Result 🎲": actual_color,
#             "You Chose 🎯": your_color,
#             "Won?": won
#         })

#         # Determine next bet
#         if win:
#             st.session_state.wins += 1
#             st.session_state.bet = bet
#             st.success(f"✅ You won! Keep your bet as ₹{bet:.2f}")
#         else:
#             st.session_state.bet = round(bet * multiplier, 2)
#             st.warning(f"❌ You lost! You should bet now with ₹{st.session_state.bet:.2f}")

#         # Check win limit
#         if st.session_state.wins >= win_stop:
#             st.session_state.active = False
#             st.success(f"🎉 You reached {win_stop} wins. Stopping strategy.")

#         st.session_state.round += 1

# # 📊 Show Table
# if st.session_state.history:
#     df = pd.DataFrame(st.session_state.history)
#     df["Net PnL ₹"] = df["Net PnL ₹"].apply(lambda x: f"-₹{abs(x):.2f}" if x < 0 else f"₹{x:.2f}")
#     st.subheader("📈 Betting History")
#     st.dataframe(df, use_container_width=True)

#     total_bet = df["Bet ₹"].sum()
#     final_pnl = df["Net PnL ₹"].iloc[-1]
#     pnl_value = float(final_pnl.replace("₹", "").replace("-", ""))
#     pnl_sign = "-" if "-" in final_pnl else "+"

#     st.markdown(f"**💸 Total Invested:** ₹{total_bet:.2f}")
#     st.markdown(f"**📊 Final Net PnL:** {final_pnl}")

#     if pnl_sign == "+":
#         st.success("🎉 You made a profit!")
#     elif pnl_sign == "-":
#         st.error("📉 You incurred a loss.")
#     else:
#         st.info("😐 No gain, no loss.")

# # 🔁 Reset
# if st.button("🔄 Reset Strategy"):
#     for key in list(st.session_state.keys()):
#         del st.session_state[key]
#     st.experimental_rerun()




#update
import streamlit as st
import pandas as pd
import random

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = []
if 'round' not in st.session_state:
    st.session_state.round = 1
if 'wallet' not in st.session_state:
    st.session_state.wallet = 0
if 'starting_bet' not in st.session_state:
    st.session_state.starting_bet = 0
if 'current_bet' not in st.session_state:
    st.session_state.current_bet = 0
if 'last_win_bet' not in st.session_state:
    st.session_state.last_win_bet = 0
if 'cumulative_pnl' not in st.session_state:
    st.session_state.cumulative_pnl = 0
if 'wins' not in st.session_state:
    st.session_state.wins = 0
if 'stop_after_wins' not in st.session_state:
    st.session_state.stop_after_wins = 0
if 'started' not in st.session_state:
    st.session_state.started = False

# UI Inputs
st.title("🎯 Color Bet Strategy")

if not st.session_state.started:
    st.session_state.wallet = st.number_input("👜 Wallet Amount ₹", min_value=100.0, value=1000.0)
    st.session_state.starting_bet = st.number_input("🎯 Starting Bet ₹", min_value=1.0, value=100.0)
    st.session_state.current_bet = st.session_state.starting_bet
    st.session_state.last_win_bet = st.session_state.starting_bet
    st.session_state.stop_after_wins = st.number_input("✅ Stop After How Many Wins", min_value=1, value=4)

color_choice = st.selectbox("🎨 Your Color Choice", ["Red", "Green", "Both"])
result_color = st.selectbox("🎲 Actual Result Color", ["Red", "Green"])

# Button to submit round
if st.button("▶️ Submit Round"):

    if st.session_state.wallet < st.session_state.current_bet:
        st.error("💰 Not enough balance in wallet.")
    elif st.session_state.wins >= st.session_state.stop_after_wins:
        st.success("🎉 You reached your win target!")
    else:
        chosen = random.choice(["Red", "Green"]) if color_choice == "Both" else color_choice
        bet = st.session_state.current_bet
        st.session_state.wallet -= bet

        win_return = 0
        pnl = 0
        won = "❌"

        if chosen == result_color:
            win_return = round(bet * 1.98, 2)
            pnl = win_return - bet
            st.session_state.wallet += win_return
            st.session_state.wins += 1
            won = "✅"
            st.session_state.last_win_bet = bet  # keep bet after win
            st.session_state.current_bet = st.session_state.last_win_bet  # keep same for next round
        else:
            pnl = -bet
            st.session_state.current_bet = round(st.session_state.current_bet * 2.25, 2)  # multiply after loss

        st.session_state.cumulative_pnl += pnl
        net_pnl_display = f"{'+' if st.session_state.cumulative_pnl >= 0 else ''}{st.session_state.cumulative_pnl:.2f}"

        # Log round data
        st.session_state.data.append({
            "Round": st.session_state.round,
            "Bet ₹": bet,
            "You Chose": chosen,
            "Result": result_color,
            "Win Return ₹": win_return,
            "Net PnL ₹": net_pnl_display,
            "Won?": won
        })

        st.session_state.round += 1
        st.session_state.started = True

# Show table
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
    st.subheader("📊 Betting History")
    st.dataframe(df, use_container_width=True)

    st.markdown(f"### 💼 Final Wallet: ₹{st.session_state.wallet:.2f}")
    st.markdown(f"### 📈 Net PnL: `{st.session_state.cumulative_pnl:+.2f} ₹`")
    st.markdown(f"### 🏆 Total Wins: {st.session_state.wins}")

# Reset
if st.button("🔁 Reset All"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()







