
import pandas as pd
import pytest

from src.synthetic.generate_passenger_journeys import (
    validate_passenger_attributes,
    validate_fare_compliance_attributes,
)


@pytest.fixture
def valid_journeys():
    """Small, valid synthetic dataset for quality tests."""
    return pd.DataFrame({
        "journey_id": ["J1", "J2", "J3"],
        "transport_mode": ["Bus", "Luas", "Rail"],
        "passenger_category": ["Adult", "Student", "Senior"],
        "payment_method": ["Leap Card", "Contactless", "Cash"],
        "fare_amount": [2.50, 1.80, 1.20],
        "validation_status": [
            "Validated",
            "Not Validated",
            "Validation Error",
        ],
        "compliance_status": [
            "Compliant",
            "Non-Compliant",
            "Validation Issue",
        ],
    })


def test_valid_passenger_attributes_pass(valid_journeys):
    validate_passenger_attributes(valid_journeys)


def test_missing_passenger_column_rejected(valid_journeys):
    invalid = valid_journeys.drop(columns=["payment_method"])

    with pytest.raises(ValueError):
        validate_passenger_attributes(invalid)


def test_null_passenger_category_rejected(valid_journeys):
    invalid = valid_journeys.copy()
    invalid.loc[0, "passenger_category"] = None

    with pytest.raises(ValueError):
        validate_passenger_attributes(invalid)


def test_valid_fare_compliance_passes(valid_journeys):
    validate_fare_compliance_attributes(valid_journeys)


def test_missing_fare_column_rejected(valid_journeys):
    invalid = valid_journeys.drop(columns=["fare_amount"])

    with pytest.raises(ValueError):
        validate_fare_compliance_attributes(invalid)


@pytest.mark.parametrize("bad_fare", [0, -2.50, None])
def test_invalid_fares_rejected(valid_journeys, bad_fare):
    invalid = valid_journeys.copy()
    invalid.loc[0, "fare_amount"] = bad_fare

    with pytest.raises(ValueError):
        validate_fare_compliance_attributes(invalid)


def test_invalid_validation_status_rejected(valid_journeys):
    invalid = valid_journeys.copy()
    invalid.loc[0, "validation_status"] = "Unknown"

    with pytest.raises(ValueError):
        validate_fare_compliance_attributes(invalid)


def test_inconsistent_compliance_rejected(valid_journeys):
    invalid = valid_journeys.copy()
    invalid.loc[0, "compliance_status"] = "Non-Compliant"

    with pytest.raises(ValueError):
        validate_fare_compliance_attributes(invalid)
