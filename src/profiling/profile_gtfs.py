from pathlib import Path
import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
GTFS_DIR = PROJECT_ROOT / "data" / "gtfs"


def list_gtfs_files():
    """Count rows in each GTFS TXT file using chunks to limit memory usage."""
    csv_files = sorted(GTFS_DIR.glob("*.txt"))

    print("GTFS files found:")
    for file in csv_files:
        print(f" - {file.name}")

    print(f"\nTotal files: {len(csv_files)}")


def inspect_gtfs_structure():
    """Inspect the columns in each GTFS file without loading the full dataset."""

    csv_files = sorted(GTFS_DIR.glob("*.txt"))

    print("\n" + "=" * 70)
    print("GTFS STRUCTURE PROFILE")
    print("=" * 70)

    for file in csv_files:
        # Only read the header row
        df = pd.read_csv(file, nrows=0)

        print(f"\n{file.name}")
        print("-" * len(file.name))

        for column in df.columns:
            print(f"  - {column}")

        print(f"Number of columns: {len(df.columns)}")


def profile_row_counts():
    """Count rows in each GTFS CSV using chunks to limit memory usage."""

    csv_files = sorted(GTFS_DIR.glob("*.txt"))

    print("\n" + "=" * 70)
    print("GTFS ROW COUNTS")
    print("=" * 70)

    for file in csv_files:
        row_count = 0

        for chunk in pd.read_csv(file, chunksize=100_000):
            row_count += len(chunk)

        print(f"{file.name:<25} {row_count:>12,} rows")

def profile_small_tables():
    """Profile missing values and duplicate rows in smaller GTFS tables."""

    large_files = {"shapes.txt", "stop_times.txt"}

    csv_files = [
        file
        for file in sorted(GTFS_DIR.glob("*.txt"))
        if file.name not in large_files
    ]

    print("\n" + "=" * 70)
    print("GTFS DATA QUALITY PROFILE - SMALL TABLES")
    print("=" * 70)

    for file in csv_files:
        df = pd.read_csv(file)

        print(f"\n{file.name}")
        print("-" * len(file.name))

        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")
        print(f"Duplicate rows: {df.duplicated().sum():,}")

        print("\nMissing values:")

        missing = df.isna().sum()
        missing = missing[missing > 0]

        if missing.empty:
            print("  None")
        else:
            for column, count in missing.items():
                percentage = (count / len(df)) * 100
                print(
                    f"  {column:<25} "
                    f"{count:>8,} "
                    f"({percentage:>6.2f}%)"
                )

def profile_key_columns():
    """Check completeness and uniqueness of important GTFS key columns."""

    key_checks = {
        "agency.txt": ["agency_id"],
        "calendar.txt": ["service_id"],
        "calendar_dates.txt": ["service_id", "date"],
        "routes.txt": ["route_id"],
        "stops.txt": ["stop_id"],
        "trips.txt": ["trip_id"],
    }

    print("\n" + "=" * 70)
    print("GTFS KEY COLUMN PROFILE")
    print("=" * 70)

    for filename, key_columns in key_checks.items():
        file_path = GTFS_DIR / filename

        df = pd.read_csv(
            file_path,
            usecols=key_columns,
            dtype=str
        )

        print(f"\n{filename}")
        print("-" * len(filename))

        for column in key_columns:
            missing = df[column].isna().sum()
            unique = df[column].nunique(dropna=True)
            duplicates = df[column].duplicated().sum()

            print(f"{column}:")
            print(f"  Missing:    {missing:,}")
            print(f"  Unique:     {unique:,}")
            print(f"  Duplicates: {duplicates:,}")

def check_referential_integrity():
    """Check whether foreign-key-like GTFS references have valid parent records."""

    print("\n" + "=" * 70)
    print("GTFS REFERENTIAL INTEGRITY CHECK")
    print("=" * 70)

    # Load only the columns required for relationship testing.
    agencies = pd.read_csv(
        GTFS_DIR / "agency.txt",
        usecols=["agency_id"],
        dtype=str
    )

    routes = pd.read_csv(
        GTFS_DIR / "routes.txt",
        usecols=["route_id", "agency_id"],
        dtype=str
    )

    calendar = pd.read_csv(
        GTFS_DIR / "calendar.txt",
        usecols=["service_id"],
        dtype=str
    )

    calendar_dates = pd.read_csv(
    GTFS_DIR / "calendar_dates.txt",
    usecols=["service_id"],
    dtype=str
)

    valid_service_ids = pd.concat(
    [calendar["service_id"], calendar_dates["service_id"]],
    ignore_index=True
).dropna().drop_duplicates()

    trips = pd.read_csv(
        GTFS_DIR / "trips.txt",
        usecols=["trip_id", "route_id", "service_id"],
        dtype=str
    )

    stops = pd.read_csv(
        GTFS_DIR / "stops.txt",
        usecols=["stop_id"],
        dtype=str
    )

    stop_times = pd.read_csv(
        GTFS_DIR / "stop_times.txt",
        usecols=["trip_id", "stop_id"],
        dtype=str
    )

    checks = [
        (
            "routes.agency_id -> agency.agency_id",
            routes["agency_id"],
            agencies["agency_id"]
        ),
        (
            "trips.route_id -> routes.route_id",
            trips["route_id"],
            routes["route_id"]
        ),
        (
            "trips.service_id -> GTFS service definitions",
            trips["service_id"],
            valid_service_ids
        ),
        (
            "stop_times.trip_id -> trips.trip_id",
            stop_times["trip_id"],
            trips["trip_id"]
        ),
        (
            "stop_times.stop_id -> stops.stop_id",
            stop_times["stop_id"],
            stops["stop_id"]
        ),
    ]

    for relationship, child, parent in checks:

        child_values = set(child.dropna())
        parent_values = set(parent.dropna())

        unmatched = child_values - parent_values

        print(f"\n{relationship}")
        print("-" * len(relationship))
        print(f"Unique referenced IDs: {len(child_values):,}")
        print(f"Unmatched IDs:         {len(unmatched):,}")

        if unmatched:
            print("Example unmatched IDs:")
            for value in list(sorted(unmatched))[:10]:
                print(f"  - {value}")
        else:
            print("Status: PASS")

def check_unused_parent_records():
    """Identify valid GTFS parent records that are not referenced downstream."""

    print("\n" + "=" * 70)
    print("GTFS UNUSED PARENT RECORD CHECK")
    print("=" * 70)

    agencies = pd.read_csv(
        GTFS_DIR / "agency.txt",
        usecols=["agency_id", "agency_name"],
        dtype=str
    )

    routes = pd.read_csv(
        GTFS_DIR / "routes.txt",
        usecols=["route_id", "agency_id", "route_short_name", "route_long_name"],
        dtype=str
    )

    calendar = pd.read_csv(
        GTFS_DIR / "calendar.txt",
        usecols=["service_id"],
        dtype=str
    )

    trips = pd.read_csv(
        GTFS_DIR / "trips.txt",
        usecols=["trip_id", "route_id", "service_id"],
        dtype=str
    )

    stops = pd.read_csv(
        GTFS_DIR / "stops.txt",
        usecols=["stop_id", "stop_name"],
        dtype=str
    )

    # Agencies not used by routes

    used_agencies = set(routes["agency_id"].dropna())
    unused_agencies = agencies[
        ~agencies["agency_id"].isin(used_agencies)
    ]

    print("\nAgencies not referenced by routes")
    print("---------------------------------")
    print(f"Unused agencies: {len(unused_agencies):,}")

    if not unused_agencies.empty:
        print(unused_agencies.to_string(index=False))

    # Routes not used by trips

    used_routes = set(trips["route_id"].dropna())
    unused_routes = routes[
        ~routes["route_id"].isin(used_routes)
    ]

    print("\nRoutes not referenced by trips")
    print("------------------------------")
    print(f"Unused routes: {len(unused_routes):,}")

    if not unused_routes.empty:
        print(
            unused_routes[
                ["route_id", "agency_id",
                 "route_short_name", "route_long_name"]
            ].to_string(index=False)
        )

    # Calendar services not used by trips

    used_services = set(trips["service_id"].dropna())
    unused_services = calendar[
        ~calendar["service_id"].isin(used_services)
    ]

    print("\nCalendar services not referenced by trips")
    print("-----------------------------------------")
    print(f"Unused services: {len(unused_services):,}")

    if not unused_services.empty:
        print(unused_services.to_string(index=False))

    # Stops not used by stop_times

    used_stops = set()

    for chunk in pd.read_csv(
        GTFS_DIR / "stop_times.txt",
        usecols=["stop_id"],
        dtype=str,
        chunksize=500_000
    ):
        used_stops.update(chunk["stop_id"].dropna())

    unused_stops = stops[
        ~stops["stop_id"].isin(used_stops)
    ]

    print("\nStops not referenced by stop_times")
    print("----------------------------------")
    print(f"Unused stops: {len(unused_stops):,}")

    if not unused_stops.empty:
        print(unused_stops.head(20).to_string(index=False))

def profile_transport_network():
    """Profile GTFS operators, transport modes, routes, and trips."""

    print("\n" + "=" * 70)
    print("GTFS TRANSPORT NETWORK PROFILE")
    print("=" * 70)

    # Load the datasets required for network profiling
    agencies = pd.read_csv(
        GTFS_DIR / "agency.txt",
        dtype=str
    )

    routes = pd.read_csv(
        GTFS_DIR / "routes.txt",
        dtype=str
    )

    trips = pd.read_csv(
        GTFS_DIR / "trips.txt",
        usecols=["trip_id", "route_id"],
        dtype=str
    )

    # Convert route_type to numeric for easier mapping
    routes["route_type"] = pd.to_numeric(
        routes["route_type"],
        errors="coerce"
    )

    # Standard GTFS route type labels relevant to this feed
    mode_mapping = {
        0: "Tram",
        1: "Subway / Metro",
        2: "Rail",
        3: "Bus",
        4: "Ferry",
        5: "Cable Tram",
        6: "Aerial Lift",
        7: "Funicular",
        11: "Trolleybus",
        12: "Monorail"
    }

    routes["transport_mode"] = (
        routes["route_type"]
        .map(mode_mapping)
        .fillna("Other / Unknown")
    )

    # Operator profile

    operator_routes = (
        routes
        .groupby("agency_id")
        .agg(
            route_count=("route_id", "nunique")
        )
        .reset_index()
    )

    operator_profile = agencies.merge(
        operator_routes,
        on="agency_id",
        how="left"
    )

    operator_profile["route_count"] = (
        operator_profile["route_count"]
        .fillna(0)
        .astype(int)
    )

    print("\nOPERATORS AND ROUTE COUNTS")
    print("--------------------------")

    print(
        operator_profile[
            ["agency_id", "agency_name", "route_count"]
        ]
        .sort_values(
            "route_count",
            ascending=False
        )
        .to_string(index=False)
    )

    # Transport mode profile

    mode_profile = (
        routes
        .groupby(["route_type", "transport_mode"])
        .agg(
            route_count=("route_id", "nunique")
        )
        .reset_index()
        .sort_values(
            "route_count",
            ascending=False
        )
    )

    print("\nTRANSPORT MODES")
    print("---------------")

    print(
        mode_profile.to_string(index=False)
    )

    # Add trip counts to routes

    trip_counts = (
        trips
        .groupby("route_id")
        .agg(
            trip_count=("trip_id", "nunique")
        )
        .reset_index()
    )

    route_activity = routes.merge(
        trip_counts,
        on="route_id",
        how="left"
    )

    route_activity["trip_count"] = (
        route_activity["trip_count"]
        .fillna(0)
        .astype(int)
    )

    # Trips by transport mode

    mode_activity = (
        route_activity
        .groupby(["route_type", "transport_mode"])
        .agg(
            routes=("route_id", "nunique"),
            trips=("trip_count", "sum")
        )
        .reset_index()
        .sort_values(
            "trips",
            ascending=False
        )
    )

    print("\nNETWORK ACTIVITY BY MODE")
    print("------------------------")

    print(
        mode_activity.to_string(index=False)
    )

    # Most active routes

    top_routes = (
        route_activity[
            [
                "route_id",
                "agency_id",
                "route_short_name",
                "route_long_name",
                "transport_mode",
                "trip_count"
            ]
        ]
        .sort_values(
            "trip_count",
            ascending=False
        )
        .head(20)
    )

    print("\nTOP 20 ROUTES BY NUMBER OF TRIPS")
    print("--------------------------------")

    print(
        top_routes.to_string(index=False)
    )

if __name__ == "__main__":
    list_gtfs_files()
    inspect_gtfs_structure()
    profile_row_counts()
    profile_small_tables()
    profile_key_columns()
    check_referential_integrity()
    check_unused_parent_records()
    profile_transport_network()