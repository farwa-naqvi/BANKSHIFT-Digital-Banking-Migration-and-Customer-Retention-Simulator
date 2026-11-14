
import pandas as pd
from pathlib import Path

try:
    from .parameters import (
        ELIGIBLE_CUSTOMERS,
        BRANCH_COST,
        DIGITAL_COST,
        AVAILABLE_BUDGET,
        DEFAULT_MIGRATION_MONTHS,
        SCENARIOS_FILE,
        RESULTS_FILE,
        CUSTOM_RESULTS_FILE,
        SENSITIVITY_RESULTS_FILE
    )
except ImportError:
    from parameters import (
        ELIGIBLE_CUSTOMERS,
        BRANCH_COST,
        DIGITAL_COST,
        AVAILABLE_BUDGET,
        DEFAULT_MIGRATION_MONTHS,
        SCENARIOS_FILE,
        RESULTS_FILE,
        CUSTOM_RESULTS_FILE,
        SENSITIVITY_RESULTS_FILE
    )

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_FOLDER = PROJECT_DIR / "data" / "processed"


def load_scenarios():
    if not SCENARIOS_FILE.exists():
        raise FileNotFoundError(
            f"Scenario file not found: {SCENARIOS_FILE}"
        )

    df = pd.read_csv(SCENARIOS_FILE)

    required_columns = [
        "Strategy",
        "Adoption_Rate",
        "Attrition_Rate",
        "Support_Cost",
        "Implementation_Cost",
        "Migration_Months"
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Missing scenario column: {column}"
            )

    if df.empty:
        raise ValueError("No migration scenarios found.")

    return df


def calculate_scenario(
    name,
    assumptions,
    eligible_customers=ELIGIBLE_CUSTOMERS,
    branch_cost=BRANCH_COST,
    digital_cost=DIGITAL_COST,
    available_budget=AVAILABLE_BUDGET
):
    adoption_rate = float(assumptions["adoption_rate"])
    attrition_rate = float(assumptions["attrition_rate"])
    support_cost = float(assumptions["support_cost"])
    implementation_cost = float(assumptions["implementation_cost"])
    migration_months = int(assumptions["migration_months"])

    if not 0 <= adoption_rate <= 1:
        raise ValueError("Adoption rate must be between 0 and 1.")

    if not 0 <= attrition_rate <= 1:
        raise ValueError("Attrition rate must be between 0 and 1.")

    if migration_months < 1 or migration_months > 12:
        raise ValueError("Migration duration must be between 1 and 12 months.")

    numeric_values = [
        eligible_customers,
        branch_cost,
        digital_cost,
        support_cost,
        implementation_cost
    ]

    if any(value < 0 for value in numeric_values):
        raise ValueError("Customer count and costs cannot be negative.")

    if available_budget <= 0:
        raise ValueError("Available budget must be greater than zero.")

    expected_adopters = eligible_customers * adoption_rate

    retained_adopters = (
        expected_adopters * (1 - attrition_rate)
    )

    savings_per_customer = branch_cost - digital_cost

    annual_savings = (
        retained_adopters * savings_per_customer
    )

    # Assumes customers migrate gradually and evenly
    # throughout the selected rollout period.
    first_year_savings_factor = (
        12 - migration_months / 2
    ) / 12

    first_year_savings = (
        annual_savings * first_year_savings_factor
    )

    support_expenditure = (
        expected_adopters * support_cost
    )

    total_expenditure = (
        support_expenditure + implementation_cost
    )

    net_benefit = (
        first_year_savings - total_expenditure
    )

    budget_utilisation = (
        total_expenditure / available_budget
    ) * 100

    budget_remaining = (
        available_budget - total_expenditure
    )

    return {
        "Strategy": name,
        "Eligible_Customers": int(eligible_customers),
        "Adoption_Rate": round(adoption_rate * 100, 2),
        "Attrition_Rate": round(attrition_rate * 100, 2),
        "Migration_Months": migration_months,
        "Expected_Adopters": round(expected_adopters),
        "Retained_Adopters": round(retained_adopters),
        "Annual_Savings_Run_Rate": round(annual_savings),
        "First_Year_Savings": round(first_year_savings),
        "Support_Expenditure": round(support_expenditure),
        "Implementation_Cost": round(implementation_cost),
        "Migration_Expenditure": round(total_expenditure),
        "Net_First_Year_Benefit": round(net_benefit),
        "Budget_Utilisation": round(budget_utilisation, 2),
        "Budget_Remaining": round(budget_remaining),
        "Budget_Status": (
            "Within Budget"
            if total_expenditure <= available_budget
            else "Over Budget"
        )
    }


def run_simulation():
    scenarios = load_scenarios()
    results = []

    for _, row in scenarios.iterrows():
        assumptions = {
            "adoption_rate": row["Adoption_Rate"],
            "attrition_rate": row["Attrition_Rate"],
            "support_cost": row["Support_Cost"],
            "implementation_cost": row["Implementation_Cost"],
            "migration_months": row["Migration_Months"]
        }

        result = calculate_scenario(
            name=row["Strategy"],
            assumptions=assumptions
        )

        results.append(result)

    return pd.DataFrame(results)


def run_custom_simulation(
    eligible_customers,
    adoption_rate,
    attrition_rate,
    branch_cost,
    digital_cost,
    support_cost,
    implementation_cost,
    available_budget,
    migration_months=DEFAULT_MIGRATION_MONTHS
):
    assumptions = {
        "adoption_rate": adoption_rate,
        "attrition_rate": attrition_rate,
        "support_cost": support_cost,
        "implementation_cost": implementation_cost,
        "migration_months": migration_months
    }

    result = calculate_scenario(
        name="Custom Strategy",
        assumptions=assumptions,
        eligible_customers=eligible_customers,
        branch_cost=branch_cost,
        digital_cost=digital_cost,
        available_budget=available_budget
    )

    return pd.DataFrame([result])


def run_sensitivity_analysis(
    eligible_customers,
    adoption_rate,
    attrition_rate,
    branch_cost,
    digital_cost,
    support_cost,
    implementation_cost,
    available_budget,
    migration_months
):
    base_assumptions = {
        "adoption_rate": adoption_rate,
        "attrition_rate": attrition_rate,
        "support_cost": support_cost,
        "implementation_cost": implementation_cost,
        "migration_months": migration_months
    }

    test_values = {
        "Adoption Rate": sorted(set(
            max(0, min(1, adoption_rate + change))
            for change in [-0.20, -0.10, 0, 0.10, 0.20]
        )),
        "Attrition Rate": sorted(set(
            max(0, min(1, attrition_rate + change))
            for change in [-0.10, -0.05, 0, 0.05, 0.10]
        )),
        "Support Cost": sorted(set(
            max(0, round(support_cost * multiplier))
            for multiplier in [0.5, 0.75, 1, 1.25, 1.5]
        )),
        "Migration Duration": sorted(set(
            max(1, min(12, migration_months + change))
            for change in [-4, -2, 0, 2, 4]
        ))
    }

    results = []

    for factor, values in test_values.items():
        for value in values:
            assumptions = base_assumptions.copy()

            if factor == "Adoption Rate":
                assumptions["adoption_rate"] = value
                display_value = value * 100

            elif factor == "Attrition Rate":
                assumptions["attrition_rate"] = value
                display_value = value * 100

            elif factor == "Support Cost":
                assumptions["support_cost"] = value
                display_value = value

            else:
                assumptions["migration_months"] = value
                display_value = value

            result = calculate_scenario(
                name="Sensitivity Test",
                assumptions=assumptions,
                eligible_customers=eligible_customers,
                branch_cost=branch_cost,
                digital_cost=digital_cost,
                available_budget=available_budget
            )

            results.append({
                "Factor": factor,
                "Tested_Value": display_value,
                "Net_First_Year_Benefit": result[
                    "Net_First_Year_Benefit"
                ],
                "Migration_Expenditure": result[
                    "Migration_Expenditure"
                ],
                "Budget_Utilisation": result[
                    "Budget_Utilisation"
                ],
                "Expected_Adopters": result[
                    "Expected_Adopters"
                ],
                "First_Year_Savings": result[
                    "First_Year_Savings"
                ]
            })

    return pd.DataFrame(results)


def save_results(results, filename):
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_FOLDER / filename
    results.to_csv(output_path, index=False)

    return output_path


if __name__ == "__main__":
    results = run_simulation()

    print("\nBANKSHIFT - PREDEFINED STRATEGY RESULTS\n")
    print(results.to_string(index=False))

    custom_result = run_custom_simulation(
        eligible_customers=10000,
        adoption_rate=0.50,
        attrition_rate=0.10,
        branch_cost=12000,
        digital_cost=4000,
        support_cost=1800,
        implementation_cost=2000000,
        available_budget=15000000,
        migration_months=6
    )

    print("\nCUSTOM SIMULATION RESULTS\n")
    print(custom_result.to_string(index=False))

    sensitivity = run_sensitivity_analysis(
        eligible_customers=10000,
        adoption_rate=0.50,
        attrition_rate=0.10,
        branch_cost=12000,
        digital_cost=4000,
        support_cost=1800,
        implementation_cost=2000000,
        available_budget=15000000,
        migration_months=6
    )

    print("\nSENSITIVITY ANALYSIS\n")
    print(sensitivity.to_string(index=False))

    print("\nFILES SAVED:")
    print(save_results(results, RESULTS_FILE))
    print(save_results(custom_result, CUSTOM_RESULTS_FILE))
    print(save_results(sensitivity, SENSITIVITY_RESULTS_FILE))
