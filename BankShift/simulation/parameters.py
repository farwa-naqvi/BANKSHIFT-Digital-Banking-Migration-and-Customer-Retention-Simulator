from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"

ELIGIBLE_CUSTOMERS = 10000

BRANCH_COST = 12000
DIGITAL_COST = 4000

AVAILABLE_BUDGET = 15000000

DEFAULT_MIGRATION_MONTHS = 6

SCENARIOS_FILE = Path(__file__).resolve().parent / "migration_scenarios.csv"

RESULTS_FILE = "migration_simulation_results.csv"
CUSTOM_RESULTS_FILE = "custom_migration_simulation.csv"
SENSITIVITY_RESULTS_FILE = "migration_sensitivity_analysis.csv"