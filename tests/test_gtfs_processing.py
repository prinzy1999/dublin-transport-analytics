
import pandas as pd

from src.processing.build_dublin_subset import (
    identify_dublin_stops,
    build_core_dublin_network,
)


def test_identify_dublin_stops():
    """Only stops inside the Dublin study area should be selected."""

    stops = pd.DataFrame({
        "stop_id": ["S1", "S2", "S3"],
        "stop_name": ["Dublin Centre", "Outside Dublin", "Invalid"],
        "stop_lat": ["53.35", "52.00", "unknown"],
        "stop_lon": ["-6.26", "-7.00", "-6.20"],
    })

    result = identify_dublin_stops(stops)

    assert result["stop_id"].tolist() == ["S1"]
    assert pd.api.types.is_numeric_dtype(result["stop_lat"])
    assert pd.api.types.is_numeric_dtype(result["stop_lon"])


def test_core_network_preserves_complete_trips():
    """
    Retained routes must keep all their stops,
    including stops outside the Dublin study area.
    """

    agency = pd.DataFrame({
        "agency_id": ["A1", "A2"],
        "agency_name": ["Operator One", "Operator Two"],
    })

    routes = pd.DataFrame({
        "route_id": ["R1", "R2"],
        "agency_id": ["A1", "A2"],
        "route_type": ["3", "3"],
    })

    trips = pd.DataFrame({
        "trip_id": ["T1", "T2"],
        "route_id": ["R1", "R2"],
    })

    stops = pd.DataFrame({
        "stop_id": ["S1", "S2", "S3"],
    })

    stop_times = pd.DataFrame({
        "trip_id": ["T1", "T1", "T2"],
        "stop_id": ["S1", "S2", "S3"],
        "stop_sequence": ["1", "2", "1"],
    })

    route_coverage = pd.DataFrame({
        "route_id": ["R1", "R2"],
        "dublin_coverage_pct": [75.0, 50.0],
    })

    (
        core_agency,
        core_routes,
        core_trips,
        core_stop_times,
        core_stops,
        selected_coverage,
    ) = build_core_dublin_network(
        agency,
        routes,
        trips,
        stop_times,
        stops,
        route_coverage,
    )

    assert set(core_routes["route_id"]) == {"R1"}
    assert set(core_trips["trip_id"]) == {"T1"}
    assert set(core_stop_times["stop_id"]) == {"S1", "S2"}
    assert set(core_stops["stop_id"]) == {"S1", "S2"}
    assert set(core_agency["agency_id"]) == {"A1"}
    assert selected_coverage["route_id"].tolist() == ["R1"]
