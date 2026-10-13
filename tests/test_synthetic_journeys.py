
import pandas as pd
import pytest

from src.synthetic.generate_passenger_journeys import (
    prepare_stop_times,
    identify_usable_trips,
    build_trip_stop_lookup,
    generate_origin_destination_journeys,
    validate_synthetic_journeys,
    add_passenger_attributes,
    add_fare_compliance_attributes,
    validate_fare_compliance_attributes,
)


@pytest.fixture
def sample_network():
    trips = pd.DataFrame({
        "trip_id": ["T1", "T2"],
        "route_id": ["R1", "R2"],
        "service_id": ["WK", "WK"],
    })

    stops = pd.DataFrame({
        "stop_id": ["S1", "S2", "S3"],
        "stop_name": ["First", "Second", "Third"],
    })

    stop_times = pd.DataFrame({
        "trip_id": ["T1", "T1", "T1", "T2"],
        "stop_id": ["S1", "S2", "S3", "S1"],
        "stop_sequence": ["1", "2", "3", "1"],
    })

    return trips, stops, stop_times


def test_prepare_stop_times_sorts_sequences(sample_network):
    _, _, stop_times = sample_network

    shuffled = stop_times.iloc[::-1].reset_index(drop=True)
    result = prepare_stop_times(shuffled)

    t1 = result[result["trip_id"] == "T1"]

    assert t1["stop_sequence"].tolist() == [1, 2, 3]


def test_identify_usable_trips(sample_network):
    trips, _, stop_times = sample_network

    prepared = prepare_stop_times(stop_times)
    usable = identify_usable_trips(trips, prepared)

    assert set(usable["trip_id"]) == {"T1"}


def test_generated_journeys_have_valid_stop_order(sample_network):
    trips, stops, stop_times = sample_network

    prepared = prepare_stop_times(stop_times)
    usable = identify_usable_trips(trips, prepared)

    lookup = build_trip_stop_lookup(
        usable, prepared, stops
    )

    journeys = generate_origin_destination_journeys(
        usable_trips=usable,
        trip_stop_lookup=lookup,
        journey_count=20,
        valid_service_dates={"WK": [pd.Timestamp("2026-10-01").date()]},
        random_seed=42,
    )

    assert len(journeys) == 20
    assert journeys["journey_id"].is_unique
    assert (
        journeys["destination_stop_sequence"]
        > journeys["origin_stop_sequence"]
    ).all()

    validate_synthetic_journeys(journeys)


def test_passenger_attributes_are_reproducible():
    journeys = pd.DataFrame({
        "journey_id": ["J1", "J2", "J3"],
        "transport_mode": ["Bus", "Luas", "Rail"],
    })

    first = add_passenger_attributes(journeys, random_seed=42)
    second = add_passenger_attributes(journeys, random_seed=42)

    pd.testing.assert_frame_equal(first, second)

    assert first["passenger_category"].notna().all()
    assert first["payment_method"].notna().all()


def test_fare_compliance_is_consistent():
    journeys = pd.DataFrame({
        "transport_mode": ["Bus", "Luas", "Rail"] * 10,
        "passenger_category": ["Adult", "Student", "Senior"] * 10,
        "payment_method": ["Leap Card"] * 30,
    })

    result = add_fare_compliance_attributes(
        journeys, random_seed=42
    )

    assert (result["fare_amount"] > 0).all()

    expected = {
        "Validated": "Compliant",
        "Not Validated": "Non-Compliant",
        "Validation Error": "Validation Issue",
    }

    assert all(
        expected[validation] == compliance
        for validation, compliance in zip(
            result["validation_status"],
            result["compliance_status"],
        )
    )

    validate_fare_compliance_attributes(result)


def test_duplicate_journey_ids_are_rejected():
    journeys = pd.DataFrame({
        "journey_id": ["J1", "J1"],
        "trip_id": ["T1", "T1"],
        "route_id": ["R1", "R1"],
        "origin_stop_id": ["S1", "S1"],
        "origin_stop_sequence": [1, 1],
        "destination_stop_id": ["S2", "S2"],
        "destination_stop_sequence": [2, 2],
    })

    with pytest.raises(ValueError):
        validate_synthetic_journeys(journeys)
