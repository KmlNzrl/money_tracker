import streamlit as st
import pandas as pd
from datetime import date
import math

from db.crud import add_transaction, get_transactions, delete_transaction, get_categories
from db.crud import add_savings_goal, get_savings_goals, update_savings_goal, delete_savings_goal, get_savings_total, get_savings_total_by_goal

# Set page config
st.set_page_config(page_title="Money Tracker", layout="wide")

st.markdown("<h1 style='text-align: center; color: white;'>💰PERSONEL MONEY TRACKER 💰</h1>", unsafe_allow_html=True)


# Load categories
categories = get_categories()
category_dict = {name: cid for cid, name in categories}
savings_goal_dict = {row[1]: row[0] for row in get_savings_goals()}

# Add transaction form
st.subheader("➕ Add New Transaction")

with st.form("add_transaction_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        date = st.date_input("Date")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")

    with col2:
        tx_type = st.selectbox("Type", ["Income", "Expense"])
        category = st.selectbox("Category", category_dict.keys())

    with col3:
        savings_goal = st.selectbox("Savings Goal", ["None"] + [g[1] for g in get_savings_goals()])
        description = st.text_input("Description")

    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        # Handle "None" selection for savings goal
        selected_goal_id = savings_goal_dict[savings_goal] if savings_goal != "None" else None
        
        add_transaction(
            date=date,
            amount=amount,
            tx_type=tx_type,
            savings_goal_id=selected_goal_id,
            category_id=category_dict[category],
            description=description
        )
        st.success('Transaction added!', icon="✅")
        st.rerun()

# Display transactions table
st.subheader("📋 Transactions")
rows = get_transactions()
df = pd.DataFrame(
    rows,
    columns=["ID", "Date", "Amount", "Type", "Savings Goal", "Category", "Description"]
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
income = df[df["Type"] == "Income"]["Amount"].sum()
expense = df[df["Type"] == "Expense"]["Amount"].sum()
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

# Display savings goals and progress bar
goals = get_savings_goals()

for goal in goals:
    goal_id, name, target, current, start, end = goal
    saved_f = float(get_savings_total_by_goal(goal_id))
    target_f = float(target)

    # Planned monthly savings, start -> end
    total_days = (end - start).days
    total_months = max(math.ceil(total_days / 30),1)
    planned_monthly = target_f / total_months
    
    # Required monthly savings, now -> end
    today = date.today()
    remaining_amount = max(target_f - saved_f, 0)
    if end > today:
        remaining_days = (end - today).days
        remaining_months = max(math.ceil(remaining_days / 30),1)
    else:
        remaining_months = 0
    required_monthly = (
        remaining_amount / remaining_months
        if remaining_months > 0
        else 0
    )

    progress = min(saved_f / target_f, 1.0) if target_f > 0 else 0

    with st.expander(f"💰 {name}", expanded=False):

        col1, col2, col3 = st.columns(3)
        col1.write(f"🎯 Target: RM {target:.2f}")
        col2.write(f"💰 Saved: RM {saved_f:.2f}")
        col3.write(f"📅 {start} → {end}")

        st.progress(progress)
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "📆 Total Duration",
            f"{total_months} months"
        )

        col2.metric(
            "🗓 Planned / Month",
            f"RM {planned_monthly:.2f}"
        )

        col3.metric(
            "⚠️ Required Now / Month",
            f"RM {required_monthly:.2f}"
        )

        st.caption(f"Remaining: RM {target_f - saved_f:.2f}")

        # 🔽 ADD MONEY SECTION (CORRECT PLACE)
        st.markdown("### 💵 Add Money to This Goal")

        with st.form(f"add_money_{goal_id}"):

            save_amount = st.number_input(
                "Amount (RM)",
                min_value=0.0,
                format="%.2f",
                key=f"amount_{goal_id}"
            )

            note = st.text_input(
                "Description",
                value=f"Savings for {name}",
                key=f"note_{goal_id}"
            )

            if st.form_submit_button("Add to Savings"):
                add_transaction(
                    date=pd.Timestamp.today().date(),
                    amount=save_amount,
                    tx_type="Expense",
                    savings_goal_id=goal_id,
                    category_id=category_dict["Savings"],
                    description=note
                )
                st.success("Money added to savings!")
                st.rerun()
        st.markdown("### ✏️ Edit Savings Goal")

        with st.form(f"edit_goal_{goal_id}"):

            new_name = st.text_input(
                "Goal Name",
                value=name,
                key=f"name_{goal_id}"
            )

            new_target = st.number_input(
                "Target Amount (RM)",
                min_value=0.0,
                value=float(target_f),
                format="%.2f",
                key=f"target_{goal_id}"
            )

            new_start = st.date_input(
                "Start Date",
                value=start,
                key=f"start_{goal_id}"
            )

            new_end = st.date_input(
                "Target Date",
                value=end,
                key=f"end_{goal_id}"
            )

            if st.form_submit_button("Update Goal"):
                update_savings_goal(
                    goal_id,
                    new_name,
                    new_target,
                    new_start,
                    new_end
                )
                st.success("Savings goal updated!")
                st.rerun()

        st.markdown("### 🗑 Delete Savings Goal")

        if st.button("Delete Goal", key=f"delete_{goal_id}"):
            delete_savings_goal(goal_id)
            st.warning("Savings goal deleted!")
            st.rerun()



