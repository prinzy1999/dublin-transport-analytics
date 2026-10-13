from pathlib import Path
import pandas as pd

# Project paths

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GTFS_DIR = PROJECT_ROOT / "data" / "gtfs"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "dublin"
# Minimum percentage of a route's scheduled stop activity
# that must occur within the Dublin study area for the route
# to be included in the core analytical network.
DUBLIN_ROUTE_COVERAGE_THRESHOLD = 75.0

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load the core GTFS tables

def load_gtfs_tables():
    """Load the GTFS tables required to build the Dublin subset."""

    print("=" * 60)
    print("LOADING GTFS DATA")
    print("=" * 60)

    agency = pd.read_csv(GTFS_DIR / "agency.txt",dtype=str)

    routes = pd.read_csv(GTFS_DIR / "routes.txt",dtype=str)

    trips = pd.read_csv(GTFS_DIR / "trips.txt",dtype=str)

    stops = pd.read_csv(GTFS_DIR / "stops.txt",dtype=str)

    # stop_times is very large, so only loading the columns
    # this is required for identifying the Dublin transport network.
    stop_times = pd.read_csv(GTFS_DIR / "stop_times.txt",dtype=str,
        usecols=["trip_id","stop_id","stop_sequence",],)

    print(f"Agencies loaded:   {len(agency):,}")
    print(f"Routes loaded:     {len(routes):,}")
    print(f"Trips loaded:      {len(trips):,}")
    print(f"Stops loaded:      {len(stops):,}")
    print(f"Stop times loaded: {len(stop_times):,}")

    return agency, routes, trips, stops, stop_times

# Inspect potential Dublin agencies

def inspect_dublin_agencies(agency):
    """Display agencies whose names contain Dublin-related keywords."""

    print("\n" + "=" * 60)
    print("DUBLIN AGENCY CANDIDATES")
    print("=" * 60)

    keywords = ["Dublin", "LUAS", "Irish Rail", "Iarnród", "Go-Ahead", "Swords",]

    pattern = "|".join(keywords)

    candidates = agency[agency["agency_name"].str.contains(pattern,case=False,na=False,)
    ].copy()

    candidates = candidates.sort_values("agency_name")

    print(candidates[["agency_id","agency_name",]].to_string(index=False))

    print(f"\nCandidate agencies found: {len(candidates):,}")

    return candidates

# Identifying stops geographically located in Dublin

def identify_dublin_stops(stops):
    """Identify GTFS stops located within the Dublin study area."""

    print("\n" + "=" * 60)
    print("DUBLIN GEOGRAPHIC STOP FILTER")
    print("=" * 60)

    stops = stops.copy()

    # Converting coordinates to numeric values.
    stops["stop_lat"] = pd.to_numeric(stops["stop_lat"],errors="coerce",)

    stops["stop_lon"] = pd.to_numeric(stops["stop_lon"],errors="coerce",)

    # Broad Dublin study-area bounding box.
    DUBLIN_LAT_MIN = 53.20
    DUBLIN_LAT_MAX = 53.65
    DUBLIN_LON_MIN = -6.65
    DUBLIN_LON_MAX = -5.95

    dublin_stops = stops[
        stops["stop_lat"].between(DUBLIN_LAT_MIN,DUBLIN_LAT_MAX,)
        & stops["stop_lon"].between(DUBLIN_LON_MIN,DUBLIN_LON_MAX,)].copy()

    print(f"Total GTFS stops:      {len(stops):,}")
    print(f"Dublin-area stops:     {len(dublin_stops):,}")

    print(f"Percentage retained:   "f"{len(dublin_stops) / len(stops) * 100:.2f}%")

    print("\nCoordinate range of retained stops:")

    print(f"Latitude:  " f"{dublin_stops['stop_lat'].min():.6f} to " f"{dublin_stops['stop_lat'].max():.6f}")

    print(f"Longitude: " f"{dublin_stops['stop_lon'].min():.6f} to "
        f"{dublin_stops['stop_lon'].max():.6f}")

    print("\nSample Dublin-area stops:")

    sample_columns = ["stop_id", "stop_name", "stop_lat", "stop_lon",]

    print(dublin_stops[sample_columns].head(20).to_string(index=False))

    return dublin_stops

# Identifying the transport network serving Dublin

def identify_dublin_network(agency, routes, trips, stop_times, dublin_stops,):
    """
    Identify trips, routes and agencies serving stops
    inside the Dublin study area.
    """

    print("\n" + "=" * 60)
    print("DUBLIN TRANSPORT NETWORK IDENTIFICATION")
    print("=" * 60)

    # Identifying stop-time records at Dublin stops

    dublin_stop_ids = set(dublin_stops["stop_id"].dropna().unique())

    dublin_stop_times = stop_times[stop_times["stop_id"].isin(dublin_stop_ids)].copy()

    print(f"Dublin stop-time records: "f"{len(dublin_stop_times):,}")

   # Identifying trips serving Dublin stops
    dublin_trip_ids = set(dublin_stop_times["trip_id"].dropna().unique())

    dublin_trips = trips[trips["trip_id"].isin(dublin_trip_ids)].copy()

    print(f"Trips serving Dublin stops: "f"{len(dublin_trips):,}")

    # Identifying routes used by those trips

    dublin_route_ids = set(dublin_trips["route_id"].dropna().unique())

    dublin_routes = routes[routes["route_id"].isin(dublin_route_ids)].copy()

    print(f"Routes serving Dublin stops: "f"{len(dublin_routes):,}")

    # Identifying agencies operating those routes

    dublin_agency_ids = set(dublin_routes["agency_id"].dropna().unique())

    dublin_agencies = agency[agency["agency_id"].isin(dublin_agency_ids)].copy()

    print(f"Agencies serving Dublin stops: "f"{len(dublin_agencies):,}")

    # Displaying agencies discovered geographically

    print("\nAGENCIES SERVING THE DUBLIN STUDY AREA")
    print("-" * 60)

    print(dublin_agencies[["agency_id","agency_name",]].sort_values("agency_name")
        .to_string(index=False))

    # Map GTFS route types to readable modes
    mode_map = {"0": "Tram", "1": "Subway", "2": "Rail", "3": "Bus", "4": "Ferry",
        "5": "Cable Tram", "6": "Aerial Lift", "7": "Funicular", "11": "Trolleybus",
        "12": "Monorail",}

    dublin_routes["transport_mode"] = (dublin_routes["route_type"].map(mode_map)
        .fillna("Other"))

    # Summarise routes by mode

    print("\nDUBLIN ROUTES BY TRANSPORT MODE")
    print("-" * 60)

    mode_summary = (dublin_routes.groupby("transport_mode").size()
        .reset_index(name="route_count").sort_values("route_count",ascending=False,))

    print(mode_summary.to_string(index=False))

    # Showing routes with the most trips

    trip_counts = (dublin_trips.groupby("route_id").size().reset_index(name="trip_count"))

    route_summary = dublin_routes.merge(trip_counts,on="route_id",how="left",)

    route_summary["trip_count"] = (route_summary["trip_count"].fillna(0).astype(int))

    route_summary = route_summary.sort_values("trip_count", ascending=False,)

    print("\nTOP 20 ROUTES SERVING DUBLIN-AREA STOPS")
    print("-" * 60)

    route_columns = ["route_id", "agency_id","route_short_name","route_long_name",
        "transport_mode","trip_count",]

    print(route_summary[route_columns].head(20).to_string(index=False))

    # Validation summary

    print("\nDUBLIN NETWORK VALIDATION SUMMARY")
    print("-" * 60)

    print(f"Dublin geographic stops: "f"{len(dublin_stops):,}")

    print(f"Stop-time records at Dublin stops: "f"{len(dublin_stop_times):,}")

    print(f"Unique Dublin-serving trips: "f"{dublin_trips['trip_id'].nunique():,}")

    print(f"Unique Dublin-serving routes: "f"{dublin_routes['route_id'].nunique():,}")

    print(f"Unique Dublin-serving agencies: "f"{dublin_agencies['agency_id'].nunique():,}")

    return (dublin_agencies, dublin_routes, dublin_trips, dublin_stop_times,)


def analyse_route_dublin_coverage(routes,trips,stop_times,dublin_stops,):
    """
    Calculate the proportion of stop-time activity occurring inside
    the Dublin study area for every GTFS route.
    """

    print("\n" + "=" * 60)
    print("ROUTE-LEVEL DUBLIN COVERAGE ANALYSIS")
    print("=" * 60)

    # Creating Dublin stop lookup

    dublin_stop_ids = set(dublin_stops["stop_id"].dropna().unique())

    # Marking every stop-time record as Dublin / non-Dublin

    stop_activity = stop_times[["trip_id", "stop_id"]].copy()

    stop_activity["is_dublin_stop"] = (stop_activity["stop_id"].isin(dublin_stop_ids))

    # Attaching route_id to each stop-time record

    trip_routes = trips[["trip_id", "route_id"]].drop_duplicates()

    stop_activity = stop_activity.merge(trip_routes,on="trip_id",
        how="left",validate="many_to_one",)

    # Removing records that could not be linked to a route.
    stop_activity = stop_activity.dropna(subset=["route_id"])

    # Aggregate stop activity by route

    route_coverage = (stop_activity.groupby("route_id").agg(
            total_stop_events=("stop_id", "size"),
            dublin_stop_events=("is_dublin_stop", "sum"),).reset_index())

    route_coverage["dublin_coverage_pct"] = (
        route_coverage["dublin_stop_events"] / route_coverage["total_stop_events"]* 100)

    #  Adding route information

    route_columns = ["route_id","agency_id","route_short_name","route_long_name",
        "route_type",]

    route_coverage = route_coverage.merge(routes[route_columns], on="route_id",
        how="left", validate="one_to_one",)

    #  Adding readable transport modes

    mode_map = {"0": "Tram", "1": "Subway", "2": "Rail", "3": "Bus", "4": "Ferry",
        "5": "Cable Tram", "6": "Aerial Lift", "7": "Funicular", "11": "Trolleybus",
        "12": "Monorail",}

    route_coverage["transport_mode"] = (route_coverage["route_type"].map(mode_map)
        .fillna("Other"))

    # Keeping routes that actually touch Dublin

    dublin_touching_routes = route_coverage[route_coverage["dublin_stop_events"] > 0
    ].copy()

    print(f"Routes with at least one Dublin stop event: "
           f"{len(dublin_touching_routes):,}")

    # Coverage distribution

    print("\nDUBLIN COVERAGE DISTRIBUTION")
    print("-" * 60)

    coverage_bins = [0, 10, 25, 50, 75, 90, 99, 100.0001,]

    coverage_labels = [">0-10%", ">10-25%", ">25-50%", ">50-75%", ">75-90%",
        ">90-99%", "99-100%",]

    dublin_touching_routes["coverage_band"] = pd.cut(
        dublin_touching_routes["dublin_coverage_pct"],
        bins=coverage_bins, labels=coverage_labels, include_lowest=False,
        right=True,)

    coverage_summary = (dublin_touching_routes.groupby("coverage_band",observed=True,)
        .size().reset_index(name="route_count"))

    print(coverage_summary.to_string(index=False))

    # Coverage distribution by transport mode

    print("\nCOVERAGE BY TRANSPORT MODE")
    print("-" * 60)

    mode_coverage = (dublin_touching_routes.groupby("transport_mode")
        .agg(routes=("route_id", "nunique"), average_dublin_coverage=(
                "dublin_coverage_pct","mean",),
            median_dublin_coverage=("dublin_coverage_pct","median",),)
        .reset_index())

    mode_coverage["average_dublin_coverage"] = mode_coverage["average_dublin_coverage"
    ].round(2)

    mode_coverage["median_dublin_coverage"] = mode_coverage[
        "median_dublin_coverage"].round(2)

    print(mode_coverage.to_string(index=False))

    # Highest Dublin coverage routes

    display_columns = ["route_id", "agency_id", "route_short_name", "route_long_name",
        "transport_mode", "total_stop_events", "dublin_stop_events", "dublin_coverage_pct",]

    highest_coverage = (dublin_touching_routes.sort_values(["dublin_coverage_pct",
                "dublin_stop_events",],ascending=[False, False],))

    print("\nTOP 30 ROUTES BY DUBLIN COVERAGE")
    print("-" * 60)

    highest_display = (highest_coverage[display_columns].head(30).copy())

    highest_display["dublin_coverage_pct"] = (highest_display["dublin_coverage_pct"]
        .round(2))

    print(highest_display.to_string(index=False))

    # Lowest coverage routes touching Dublin

    lowest_coverage = (dublin_touching_routes.sort_values(
            ["dublin_coverage_pct", "dublin_stop_events",], ascending=[True, False],))

    print("\nBOTTOM 30 ROUTES BY DUBLIN COVERAGE")
    print("-" * 60)

    lowest_display = (lowest_coverage[display_columns].head(30).copy())

    lowest_display["dublin_coverage_pct"] = (lowest_display["dublin_coverage_pct"]
        .round(2))

    print(lowest_display.to_string(index=False))

    # Useful threshold comparison

    print("\nPOTENTIAL COVERAGE THRESHOLDS")
    print("-" * 60)

    for threshold in [25, 50, 75, 90, 95, 99]:
        count = (dublin_touching_routes["dublin_coverage_pct"] >= threshold
        ).sum()

        print(f"Routes with >= {threshold}% Dublin coverage: " f"{count:,}")

    return dublin_touching_routes


def build_core_dublin_network(agency, routes, trips, stop_times, stops,
    route_coverage, coverage_threshold=DUBLIN_ROUTE_COVERAGE_THRESHOLD,
):
    """
    Build the core Dublin public transport network.

    A route is retained when at least `coverage_threshold` percent
    of its scheduled stop events occur within the Dublin geographic
    study area.

    All dependent GTFS tables are then filtered from those retained
    route IDs to preserve referential consistency.
    """

    print("\n" + "=" * 60)
    print("BUILDING CORE DUBLIN ANALYTICAL NETWORK")
    print("=" * 60)

    # Select routes meeting Dublin coverage threshold

    selected_coverage = route_coverage[route_coverage["dublin_coverage_pct"]
        >= coverage_threshold].copy()

    selected_route_ids = set(selected_coverage["route_id"].dropna()
        .unique())

    core_routes = routes[routes["route_id"].isin(selected_route_ids)
    ].copy()

    # Keep trips belonging to selected routes

    core_trips = trips[trips["route_id"].isin(selected_route_ids)
    ].copy()

    core_trip_ids = set(core_trips["trip_id"].dropna().unique())

    # Keep stop-times belonging to retained trips

    core_stop_times = stop_times[stop_times["trip_id"].isin(core_trip_ids)
    ].copy()

    # Keep every stop used by those trips

    # We intentionally retain the complete route geometry rather
    # than deleting individual stops outside the geographic box.

    core_stop_ids = set(core_stop_times["stop_id"].dropna()
        .unique())

    core_stops = stops[stops["stop_id"].isin(core_stop_ids)
    ].copy()

    # Keeping agencies represented by selected routes

    core_agency_ids = set(core_routes["agency_id"].dropna().unique())

    core_agency = agency[agency["agency_id"].isin(core_agency_ids)].copy()

    # Validation

    print(f"Coverage threshold: " f"{coverage_threshold:.1f}%")

    print(f"Core agencies: " f"{core_agency['agency_id'].nunique():,}")

    print(f"Core routes: " f"{core_routes['route_id'].nunique():,}")

    print(f"Core trips: " f"{core_trips['trip_id'].nunique():,}")

    print(f"Core stops: " f"{core_stops['stop_id'].nunique():,}")

    print(f"Core stop-time records: " f"{len(core_stop_times):,}")

    # Referential integrity checks

    route_trip_failures = (set(core_trips["route_id"].dropna()) - set(core_routes["route_id"].dropna()))

    trip_stop_time_failures = (set(core_stop_times["trip_id"].dropna())
        - set(core_trips["trip_id"].dropna()))

    stop_failures = (set(core_stop_times["stop_id"].dropna())
        - set(core_stops["stop_id"].dropna()))

    print("\nCORE NETWORK REFERENTIAL INTEGRITY")
    print("-" * 60)

    print("Trips referencing missing routes:",len(route_trip_failures),)

    print("Stop-times referencing missing trips:",len(trip_stop_time_failures),)

    print("Stop-times referencing missing stops:",len(stop_failures),)

    if (len(route_trip_failures) == 0
        and len(trip_stop_time_failures) == 0
        and len(stop_failures) == 0):
        print("Status: PASS")
    else:
        print("Status: FAIL")

    # Mode summary

    mode_map = {"0": "Tram","1": "Subway","2": "Rail","3": "Bus",
        "4": "Ferry","5": "Cable Tram","6": "Aerial Lift","7": "Funicular",
        "11": "Trolleybus","12": "Monorail",}

    mode_summary = core_routes.copy()

    mode_summary["transport_mode"] = (mode_summary["route_type"].map(mode_map)
        .fillna("Other"))

    mode_summary = (mode_summary.groupby("transport_mode")
        .agg(routes=("route_id", "nunique")).reset_index()
        .sort_values("routes",ascending=False,))

    print("\nCORE NETWORK ROUTES BY MODE")
    print("-" * 60)

    print(
        mode_summary.to_string(index=False)
    )

    # Agency summary

    agency_summary = (
        core_routes[
            ["agency_id", "route_id"]
        ]
        .merge(
            core_agency[
                ["agency_id", "agency_name"]
            ],
            on="agency_id",
            how="left",
        )
        .groupby(
            ["agency_id", "agency_name"],
            dropna=False,
        )
        .agg(
            routes=("route_id", "nunique")
        )
        .reset_index()
        .sort_values(
            "routes",
            ascending=False,
        )
    )

    print("\nCORE NETWORK AGENCIES")
    print("-" * 60)

    print(
        agency_summary.to_string(index=False)
    )

    return (
        core_agency,
        core_routes,
        core_trips,
        core_stop_times,
        core_stops,
        selected_coverage,
    )

# Export the validated core Dublin GTFS network

def export_core_dublin_network(core_agency, core_routes, core_trips, core_stop_times,
    core_stops,core_route_coverage,):
    """
    Export the validated core Dublin analytical network.

    Full source GTFS tables are reloaded where necessary so that the
    exported Dublin dataset retains useful GTFS attributes that were
    excluded from the lightweight profiling stage.
    """

    print("\n" + "=" * 60)
    print("EXPORTING CORE DUBLIN ANALYTICAL NETWORK")
    print("=" * 60)

    # Create validated ID sets

    agency_ids = set(core_agency["agency_id"].dropna().unique())
    route_ids = set(core_routes["route_id"].dropna().unique())
    trip_ids = set(core_trips["trip_id"].dropna().unique())
    stop_ids = set(core_stops["stop_id"].dropna().unique())

    # Reloading complete GTFS tables.
    # stop_times was originally loaded with only the columns required
    # for network identification, so the complete table is restored here.

    full_agency = pd.read_csv(
        GTFS_DIR / "agency.txt",
        dtype=str,
    )

    full_routes = pd.read_csv(
        GTFS_DIR / "routes.txt",
        dtype=str,
    )

    full_trips = pd.read_csv(
        GTFS_DIR / "trips.txt",
        dtype=str,
    )

    full_stops = pd.read_csv(
        GTFS_DIR / "stops.txt",
        dtype=str,
    )

    full_stop_times = pd.read_csv(
        GTFS_DIR / "stop_times.txt",
        dtype=str,
    )

    # Filter complete GTFS tables using validated network IDs

    export_agency = full_agency[
        full_agency["agency_id"].isin(agency_ids)
    ].copy()

    export_routes = full_routes[
        full_routes["route_id"].isin(route_ids)
    ].copy()

    export_trips = full_trips[
        full_trips["trip_id"].isin(trip_ids)
    ].copy()

    export_stops = full_stops[
        full_stops["stop_id"].isin(stop_ids)
    ].copy()

    export_stop_times = full_stop_times[
        full_stop_times["trip_id"].isin(trip_ids)
    ].copy()

    # Final safety check: exported stop-times should only reference
    # stops belonging to the validated core network.

    export_stop_times = export_stop_times[
        export_stop_times["stop_id"].isin(stop_ids)
    ].copy()

    # Export route coverage metadata

    export_route_coverage = core_route_coverage.copy()

    # Write files

    export_tables = {
        "agency.csv": export_agency,
        "routes.csv": export_routes,
        "trips.csv": export_trips,
        "stops.csv": export_stops,
        "stop_times.csv": export_stop_times,
        "route_coverage.csv": export_route_coverage,
    }

    print(f"\nOutput directory: {OUTPUT_DIR}")

    for filename, dataframe in export_tables.items():

        output_path = OUTPUT_DIR / filename

        dataframe.to_csv(
            output_path,
            index=False,
        )

        print(
            f"{filename:<20} "
            f"{len(dataframe):>10,} rows "
            f"{len(dataframe.columns):>3} columns"
        )

    print("\nCore Dublin network export complete.")

    return export_tables

# Main

def main():

    (agency, routes, trips, stops,stop_times,) = load_gtfs_tables()

    print("\nGTFS core tables loaded successfully.")

    # Initial name-based inspection.
    # This is exploratory only and does not define the final network.
    inspect_dublin_agencies(agency)

    # Geographic identification of Dublin-area stops.
    dublin_stops = identify_dublin_stops(stops)

    # Relational identification of services touching those stops.
    (dublin_agencies, dublin_routes, dublin_trips, dublin_stop_times,) = identify_dublin_network(
        agency, routes, trips, stop_times, dublin_stops,)

    route_coverage = analyse_route_dublin_coverage(
        routes, trips, stop_times, dublin_stops,)

    (core_agency, core_routes, core_trips, core_stop_times, core_stops,
        core_route_coverage,) = build_core_dublin_network(agency, routes, trips,
        stop_times, stops,route_coverage,)

    export_core_dublin_network(core_agency, core_routes, core_trips, core_stop_times,
        core_stops, core_route_coverage,)


if __name__ == "__main__":
    main()