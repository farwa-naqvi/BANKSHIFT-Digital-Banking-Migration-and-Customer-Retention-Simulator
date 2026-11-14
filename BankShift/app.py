
import streamlit as st
import pandas as pd

from simulation.simulator import (
    run_simulation,
    run_custom_simulation,
    run_sensitivity_analysis
)

st.set_page_config(
    page_title="BANKSHIFT",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 BANKSHIFT")
st.subheader("Digital Banking Migration & Customer Retention Simulator")

st.write(
    "Evaluate digital banking migration strategies, estimate financial "
    "benefits, and explore the effect of changing business assumptions."
)

st.info(
    "This simulator uses illustrative assumptions. Its outputs are "
    "scenario estimates, not actual bank financial results or forecasts."
)

# --------------------------------------------------
# SIDEBAR: SIMULATION INPUTS
# --------------------------------------------------

st.sidebar.title("Simulation Settings")

with st.sidebar.form("simulation_form"):

    st.subheader("Customer Information")

    eligible_customers = st.number_input(
        "Eligible Customers",
        min_value=1,
        max_value=1000000,
        value=10000,
        step=500
    )

    adoption_rate = st.slider(
        "Expected Adoption Rate (%)",
        min_value=0,
        max_value=100,
        value=50,
        step=5
    )

    attrition_rate = st.slider(
        "Post-Migration Attrition Rate (%)",
        min_value=0,
        max_value=100,
        value=10,
        step=1
    )

    st.subheader("Migration Pace")

    migration_months = st.slider(
        "Migration Duration (Months)",
        min_value=1,
        max_value=12,
        value=6
    )

    st.subheader("Servicing Costs")

    branch_cost = st.number_input(
        "Annual Branch Cost per Customer (PKR)",
        min_value=0,
        value=12000,
        step=500
    )

    digital_cost = st.number_input(
        "Annual Digital Cost per Customer (PKR)",
        min_value=0,
        value=4000,
        step=500
    )

    st.subheader("Migration Costs")

    support_cost = st.number_input(
        "Support Cost per Adopter (PKR)",
        min_value=0,
        value=1800,
        step=100
    )

    implementation_cost = st.number_input(
        "Implementation Cost (PKR)",
        min_value=0,
        value=2000000,
        step=100000
    )

    available_budget = st.number_input(
        "Available Budget (PKR)",
        min_value=1,
        value=15000000,
        step=500000
    )

    run_button = st.form_submit_button(
        "Run Complete Simulation",
        type="primary"
    )


# --------------------------------------------------
# RUN CUSTOM SIMULATION
# --------------------------------------------------

if run_button:

    try:
        custom_result = run_custom_simulation(
            eligible_customers=eligible_customers,
            adoption_rate=adoption_rate / 100,
            attrition_rate=attrition_rate / 100,
            branch_cost=branch_cost,
            digital_cost=digital_cost,
            support_cost=support_cost,
            implementation_cost=implementation_cost,
            available_budget=available_budget,
            migration_months=migration_months
        )

        sensitivity_result = run_sensitivity_analysis(
            eligible_customers=eligible_customers,
            adoption_rate=adoption_rate / 100,
            attrition_rate=attrition_rate / 100,
            branch_cost=branch_cost,
            digital_cost=digital_cost,
            support_cost=support_cost,
            implementation_cost=implementation_cost,
            available_budget=available_budget,
            migration_months=migration_months
        )

        st.session_state["custom_result"] = custom_result
        st.session_state["sensitivity_result"] = sensitivity_result

        st.success("Custom simulation and sensitivity analysis completed.")

    except (ValueError, TypeError) as error:
        st.error(str(error))


# --------------------------------------------------
# DISPLAY CUSTOM SIMULATION
# --------------------------------------------------

if "custom_result" in st.session_state:

    custom_result = st.session_state["custom_result"]
    result = custom_result.iloc[0]

    st.divider()
    st.header("Custom Migration Scenario")

    st.subheader("Key Performance Indicators")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Expected Adopters",
        f"{result['Expected_Adopters']:,}"
    )

    col2.metric(
        "Retained Adopters",
        f"{result['Retained_Adopters']:,}"
    )

    col3.metric(
        "First-Year Savings",
        f"PKR {result['First_Year_Savings']:,.0f}"
    )

    col4.metric(
        "Net First-Year Benefit",
        f"PKR {result['Net_First_Year_Benefit']:,.0f}"
    )

    st.subheader("Financial Performance")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Full-Year Savings Run Rate",
        f"PKR {result['Annual_Savings_Run_Rate']:,.0f}"
    )

    col2.metric(
        "Migration Expenditure",
        f"PKR {result['Migration_Expenditure']:,.0f}"
    )

    col3.metric(
        "Budget Utilisation",
        f"{result['Budget_Utilisation']:.2f}%"
    )

    col1, col2 = st.columns(2)

    col1.metric(
        "Budget Remaining",
        f"PKR {result['Budget_Remaining']:,.0f}"
    )

    col2.metric(
        "Migration Duration",
        f"{result['Migration_Months']} months"
    )

    if result["Budget_Status"] == "Within Budget":
        st.success("The migration scenario is within the available budget.")
    else:
        st.error("The migration scenario exceeds the available budget.")

    st.subheader("Migration Cost Breakdown")

    cost_data = pd.DataFrame({
        "Cost Category": [
            "Support Expenditure",
            "Implementation Cost"
        ],
        "Amount (PKR)": [
            result["Support_Expenditure"],
            result["Implementation_Cost"]
        ]
    })

    st.bar_chart(
        cost_data.set_index("Cost Category")
    )

    st.subheader("Detailed Custom Simulation Results")

    st.dataframe(
        custom_result,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Custom Simulation Results",
        data=custom_result.to_csv(index=False).encode("utf-8"),
        file_name="bankshift_custom_results.csv",
        mime="text/csv"
    )

    # --------------------------------------------------
    # SENSITIVITY ANALYSIS
    # --------------------------------------------------

    st.divider()
    st.header("Sensitivity Analysis")

    st.write(
        "Sensitivity analysis changes one assumption at a time while "
        "keeping the other assumptions constant. This helps identify "
        "which factors have the greatest effect on the financial outcome."
    )

    sensitivity = st.session_state["sensitivity_result"]

    factors = [
        "Adoption Rate",
        "Attrition Rate",
        "Support Cost",
        "Migration Duration"
    ]

    for factor in factors:

        factor_data = sensitivity[
            sensitivity["Factor"] == factor
        ].copy()

        if factor_data.empty:
            continue

        st.subheader(factor)

        if factor in ["Adoption Rate", "Attrition Rate"]:
            factor_data["Tested_Value"] = (
                factor_data["Tested_Value"].astype(str) + "%"
            )

        elif factor == "Support Cost":
            factor_data["Tested_Value"] = (
                "PKR " + factor_data["Tested_Value"].map(
                    lambda value: f"{value:,.0f}"
                )
            )

        else:
            factor_data["Tested_Value"] = (
                factor_data["Tested_Value"].astype(int).astype(str)
                + " months"
            )

        chart_data = factor_data[
            ["Tested_Value", "Net_First_Year_Benefit"]
        ].set_index("Tested_Value")

        st.line_chart(chart_data)

        st.dataframe(
            factor_data,
            use_container_width=True,
            hide_index=True
        )

    st.download_button(
        "Download Sensitivity Analysis Results",
        data=sensitivity.to_csv(index=False).encode("utf-8"),
        file_name="bankshift_sensitivity_analysis.csv",
        mime="text/csv"
    )


# --------------------------------------------------
# PREDEFINED STRATEGY COMPARISON
# --------------------------------------------------

st.divider()
st.header("Predefined Migration Strategy Comparison")

st.write(
    "Compare the Conservative, Balanced and Aggressive strategies "
    "using the assumptions stored in migration_scenarios.csv."
)

try:
    strategy_results = run_simulation()

    st.subheader("Strategy Results")

    st.dataframe(
        strategy_results,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Net First-Year Benefit")

    benefit_data = strategy_results[
        ["Strategy", "Net_First_Year_Benefit"]
    ].set_index("Strategy")

    st.bar_chart(benefit_data)

    st.subheader("Migration Expenditure")

    expenditure_data = strategy_results[
        ["Strategy", "Migration_Expenditure"]
    ].set_index("Strategy")

    st.bar_chart(expenditure_data)

    st.subheader("Budget Utilisation")

    budget_data = strategy_results[
        ["Strategy", "Budget_Utilisation"]
    ].set_index("Strategy")

    st.bar_chart(budget_data)

    st.subheader("Budget Status")

    for _, row in strategy_results.iterrows():

        if row["Budget_Status"] == "Within Budget":
            st.success(f"{row['Strategy']}: Within Budget")
        else:
            st.warning(f"{row['Strategy']}: Over Budget")

    st.download_button(
        "Download Strategy Comparison",
        data=strategy_results.to_csv(index=False).encode("utf-8"),
        file_name="bankshift_strategy_comparison.csv",
        mime="text/csv"
    )

except (FileNotFoundError, ValueError, KeyError) as error:
    st.error(f"Unable to load strategy comparison: {error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "BANKSHIFT | Digital Banking Migration & Customer Retention Analysis"
)
