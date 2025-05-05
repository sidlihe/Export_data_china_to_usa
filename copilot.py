import streamlit as st
import pandas as pd
import math

# Initialize session state variables
if 'initial_wallet' not in st.session_state:
    st.session_state.initial_wallet = 25000
if 'wallet' not in st.session_state:
    st.session_state.wallet = 25000
if 'bets_df' not in st.session_state:
    st.session_state.bets_df = pd.DataFrame(columns=["Round", "Current Bet", "Choice", "Resulted Output", "Result", "Profit/Loss", "Next Bet", "Total P&L"])
if 'current_bet' not in st.session_state:
    st.session_state.current_bet = 10  # Default starting bet
if 'wins' not in st.session_state:
    st.session_state.wins = 0
if 'stop_wins' not in st.session_state:
    st.session_state.stop_wins = None
if 'choice' not in st.session_state:
    st.session_state.choice = "big"  # Default choice
if 'last_win_bet' not in st.session_state:
    st.session_state.last_win_bet = 10  # Default on first win

# Streamlit UI
st.title("Martingale Betting Strategy Simulator")

# User inputs
st.session_state.initial_wallet = st.number_input("Enter your wallet balance:", min_value=1, step=1, value=25000)
starting_bet = st.number_input("Enter your starting bet amount:", min_value=1, step=1, value=10)
st.session_state.stop_wins = st.number_input("Stop after how many wins?", min_value=1, step=1, value=5)
st.session_state.choice = st.selectbox("Choose your bet option:", ["big", "small"])

# Set starting values only for empty DataFrame
if st.session_state.bets_df.empty:
    st.session_state.wallet = st.session_state.initial_wallet
    st.session_state.current_bet = starting_bet
    st.session_state.last_win_bet = starting_bet

# Max losses before bankruptcy
if st.session_state.wallet > 0 and st.session_state.current_bet > 0:
    max_losses = math.floor(math.log(st.session_state.wallet / st.session_state.current_bet) / math.log(2.25))
    st.write(f"⚠️ **You can afford up to {max_losses} consecutive losses before running out of balance.**")

# Game result input
game_result = st.selectbox("Enter the actual game result:", ["big", "small"])

# Simulate round
if st.button("Update Bet Result"):
    result = "Win" if game_result == st.session_state.choice else "Loss"

    # Determine profit/loss and next bet
    if result == "Win":
        profit = round(st.session_state.current_bet * 0.98, 2)
        next_bet = st.session_state.bets_df.iloc[0]["Current Bet"] if not st.session_state.bets_df.empty else starting_bet
        st.session_state.last_win_bet = next_bet
        st.session_state.wins += 1
    else:
        profit = -st.session_state.current_bet
        next_bet = round(st.session_state.current_bet * 2.25, 2)

    # Update wallet
    st.session_state.wallet += profit

    # Calculate total P&L
    total_pnl = st.session_state.bets_df["Profit/Loss"].sum() + profit

    # Append current round
    new_bet = {
        "Round": len(st.session_state.bets_df) + 1,
        "Current Bet": st.session_state.current_bet,
        "Choice": st.session_state.choice,
        "Resulted Output": game_result,
        "Result": result,
        "Profit/Loss": profit,
        "Next Bet": next_bet,
        "Total P&L": total_pnl
    }
    st.session_state.bets_df = pd.concat([st.session_state.bets_df, pd.DataFrame([new_bet])], ignore_index=True)

    # Set the next current bet
    st.session_state.current_bet = next_bet

    # Stop condition
    if st.session_state.wins >= st.session_state.stop_wins:
        st.success(f"🎉 Stopping after {st.session_state.stop_wins} wins!")
        st.session_state.bets_df = pd.DataFrame(columns=st.session_state.bets_df.columns)
        st.session_state.wins = 0
        st.session_state.current_bet = starting_bet
        st.session_state.last_win_bet = starting_bet
        st.session_state.wallet = st.session_state.initial_wallet

# Display bets table
if not st.session_state.bets_df.empty:
    st.dataframe(st.session_state.bets_df)

# Show remaining balance and total P&L
final_pnl = st.session_state.bets_df["Profit/Loss"].sum()
calculated_wallet = st.session_state.initial_wallet + final_pnl

st.write(f"💰 **Remaining Wallet Balance:** ₹{calculated_wallet:.2f}")
st.write(f"📊 **Total P&L:** ₹{final_pnl:.2f}")
