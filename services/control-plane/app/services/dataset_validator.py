"""Dataset validation using Great Expectations."""
from typing import Dict, Optional, Tuple
import json

# Great Expectations integration
try:
    import great_expectations as ge
    GE_AVAILABLE = True
except ImportError:
    GE_AVAILABLE = False
    print("Warning: great_expectations not installed. Dataset validation will be skipped.")


class DatasetValidator:
    """Validate datasets using Great Expectations."""

    @staticmethod
    def validate_dataset(
        dataset_path: str,
        expectation_suite: Optional[Dict] = None,
        fail_fast: bool = True,
    ) -> Tuple[bool, Dict]:
        """
        Validate a dataset against expectations.

        Args:
            dataset_path: Path to dataset file (CSV, Parquet, etc.)
            expectation_suite: Great Expectations suite (JSON dict)
            fail_fast: If True, fail on first validation error

        Returns:
            Tuple of (is_valid, validation_result)
        """
        if not GE_AVAILABLE:
            return True, {"status": "skipped", "reason": "Great Expectations not available"}

        try:
            # Load dataset
            context = ge.get_context()
            datasource = context.sources.add_pandas("pandas")

            # Load data
            if dataset_path.endswith(".csv"):
                data_asset = datasource.read_csv(dataset_path)
            elif dataset_path.endswith(".parquet"):
                data_asset = datasource.read_parquet(dataset_path)
            else:
                return False, {"status": "error", "reason": f"Unsupported file type: {dataset_path}"}

            # Load or create expectation suite
            if expectation_suite:
                suite = context.add_expectation_suite(expectation_suite_name="custom_suite")
                for expectation_config in expectation_suite.get("expectations", []):
                    suite.add_expectation(expectation_config)
            else:
                # Use default suite (basic checks)
                suite = context.add_expectation_suite(expectation_suite_name="default_suite")
                # Add basic expectations
                suite.expect_table_row_count_to_be_between(min_value=1)
                suite.expect_table_columns_to_exist([])

            # Run validation
            validator = context.get_validator(batch_request=data_asset.build_batch_request(), expectation_suite=suite)
            results = validator.validate()

            is_valid = results.success
            validation_result = {
                "status": "passed" if is_valid else "failed",
                "success": is_valid,
                "statistics": results.statistics,
                "results": [
                    {
                        "expectation_type": r.expectation_config.expectation_type,
                        "success": r.success,
                        "result": r.result,
                    }
                    for r in results.results
                ],
            }

            if not is_valid and fail_fast:
                failed_expectations = [r for r in results.results if not r.success]
                validation_result["failed_expectations"] = [
                    {
                        "expectation_type": r.expectation_config.expectation_type,
                        "kwargs": r.expectation_config.kwargs,
                    }
                    for r in failed_expectations
                ]

            return is_valid, validation_result

        except Exception as e:
            return False, {"status": "error", "reason": str(e)}

    @staticmethod
    def validate_before_run(
        dataset_version_id: int,
        db_session,
        fail_fast: bool = True,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate dataset before starting a test run (gating).

        Args:
            dataset_version_id: Dataset version ID
            db_session: SQLAlchemy session
            fail_fast: If True, raise exception on validation failure

        Returns:
            Tuple of (is_valid, error_message)
        """
        from app.models.dataset import DatasetVersion

        dataset_version = db_session.query(DatasetVersion).filter(DatasetVersion.id == dataset_version_id).first()
        if not dataset_version:
            return False, f"Dataset version {dataset_version_id} not found"

        # Get dataset path (from S3 or local storage)
        # TODO: Implement actual path resolution
        dataset_path = dataset_version.storage_path  # Assuming this field exists

        # Get expectations from dataset version or project
        expectation_suite = dataset_version.expectations if hasattr(dataset_version, "expectations") else None

        is_valid, result = DatasetValidator.validate_dataset(dataset_path, expectation_suite, fail_fast)

        if not is_valid:
            error_msg = f"Dataset validation failed: {result.get('reason', 'Unknown error')}"
            if fail_fast:
                raise ValueError(error_msg)
            return False, error_msg

        return True, None
