import streamlit as st
import pandas as pd

from db.crud import add_transaction, get_transactions, delete_transaction, get_categories
from db.crud import add_savings_goal, get_savings_goals, update_savings_amount

# Set page config
st.set_page_config(page_title="Money Tracker", layout="wide")

st.title("💰PERSONEL MONEY TRACKER 💰")
st.write("Track your income, expenses, and savings easily.")

# Load categories
categories = get_categories()
category_dict = {name: cid for cid, name in categories}

# Add transaction form
st.subheader("➕ Add New Transaction")

with st.form("add_transaction_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")

    with col2:
        tx_type = st.selectbox("Type", ["income", "expense"])
        category = st.selectbox("Category", category_dict.keys())

    with col3:
        description = st.text_input("Description")

    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        add_transaction(
            date=date,
            amount=amount,
            tx_type=tx_type,
            category_id=category_dict[category],
            description=description
        )
        st.success("Transaction added!")
        st.rerun()

# Display transactions table
st.subheader("📋 Transactions")

rows = get_transactions()

df = pd.DataFrame(
    rows,
    columns=["ID", "Date", "Amount", "Type", "Category", "Description"]
)

st.dataframe(df, use_container_width="stretch")

# Delete transaction
st.subheader("🗑 Delete Transaction")

tx_ids = df["ID"].tolist()

selected_id = st.selectbox("Select Transaction ID", tx_ids)

if st.button("Delete"):
    delete_transaction(selected_id)
    st.success("Transaction deleted!")
    st.rerun()

# Monthly Summary
st.subheader("📅 Monthly Summary")

income = df[df["Type"] == "income"]["Amount"].sum()
expense = df[df["Type"] == "expense"]["Amount"].sum()
balance = income - expense

col1, col2, col3 = st.columns(3)

col1.metric("Total Income", f"RM {income:.2f}")
col2.metric("Total Expense", f"RM {expense:.2f}")
col3.metric("Balance", f"RM {balance:.2f}")

# Add new savings goal form
st.subheader("🎯 Add New Savings Goal")
with st.form("add_savings_goal_form"):
    col1, col2 = st.columns(2)

    with col1:
        goal_name = st.text_input("Goal Name (e.g. Emergency Fund)")
        target_amount = st.number_input(
            "Target Amount (RM)",
            min_value=0.0,
            format="%.2f"
        )

    with col2:
        start_date = st.date_input("Start Date")
        target_date = st.date_input("Target Date")

    submitted = st.form_submit_button("Create Goal")

    if submitted:
        add_savings_goal(
            goal_name=goal_name,
            target_amount=target_amount,
            start_date=start_date,
            target_date=target_date
        )
        st.success("Savings goal created!")
        st.rerun()

# Display savings goals ang progress bar
goals = get_savings_goals()

for goal in goals:
    goal_id, name, target, current, start, end = goal

    progress = 0
    if target > 0:
        progress = min(current / target, 1.0)

    st.subheader(name)

    col1, col2, col3 = st.columns(3)
    col1.write(f"🎯 Target: RM {target:.2f}")
    col2.write(f"💰 Saved: RM {current:.2f}")
    col3.write(f"📅 Period: {start} → {end}")

    st.progress(progress)

    remaining = target - current
    st.caption(f"Remaining: RM {remaining:.2f}")

    # Add money to savings goal
    st.subheader("💰 Add Money to Savings Goal")
    add_amount = st.number_input(
        "Amount to add (RM)",
        min_value=0.0,
        format="%.2f",
        key=f"add_{goal_id}"
    )

    if st.button("Add to Savings", key=f"btn_{goal_id}"):
        update_savings_amount(goal_id, add_amount)
        st.success("Savings updated!")
        st.rerun()