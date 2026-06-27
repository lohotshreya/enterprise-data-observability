import os
import json
import shutil
import pandas as pd
from great_expectations.core.expectation_suite import ExpectationSuite
from great_expectations.dataset import PandasDataset

class DataIngestionEngine:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        
        for path in [self.config["raw_dir"], self.config["clean_dir"], self.config["quarantine_dir"]]:
            os.makedirs(path, exist_ok=True)

    def build_expectation_suite(self) -> ExpectationSuite:
        """Defines strict enterprise data quality rules."""
        suite = ExpectationSuite(expectation_suite_name="corporate_signups_suite")
        suite.add_expectation({
            "expectation_type": "expect_column_values_to_not_be_null",
            "kwargs": {"column": "user_id"}
        })
        suite.add_expectation({
            "expectation_type": "expect_column_values_to_be_of_type",
            "kwargs": {"column": "age", "type_": "int64"}
        })
        suite.add_expectation({
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {"column": "age", "min_value": 18, "max_value": 100}
        })
        return suite

    def validate_file(self, file_path: str) -> tuple[bool, pd.DataFrame | None]:
        """Validates incoming CSV file structural rules."""
        try:
            df = pd.read_csv(file_path)
            suite = self.build_expectation_suite()
            gx_df = PandasDataset(df, expectation_suite=suite)
            validation_results = gx_df.validate()

            if validation_results["success"]:
                return True, df
            else:
                print(f"[!] Validation failed for {file_path}. Quarantining.")
                shutil.move(file_path, os.path.join(self.config["quarantine_dir"], os.path.basename(file_path)))
                return False, None
        except Exception as e:
            print(f"[X] Hard structural breakdown processing {file_path}: {e}")
            shutil.move(file_path, os.path.join(self.config["quarantine_dir"], os.path.basename(file_path)))
            return False, None
