# Dublin Public Transport Fare Compliance & Passenger Journey Analytics

**End-to-end transport data analytics project | Python · Databricks · SQL · Power BI · Pytest · GitHub Actions**

A portfolio project combining publicly available National Transport Authority (NTA) GTFS data with synthetic passenger journey records to analyse Dublin public transport demand, journey patterns and simulated fare compliance.

**Project Status:** Data pipeline, Power BI report and automated testing implemented. All 18 automated tests passed locally and through GitHub Actions.

## Project Overview

This project develops an end-to-end data analytics pipeline for exploring public transport networks and passenger journey patterns across Dublin, Ireland.

It combines publicly available General Transit Feed Specification (GTFS) data published by Ireland's National Transport Authority (NTA) with synthetically generated passenger journey records.

The project demonstrates how transport data can be processed, validated, transformed and visualised to support evidence-based analysis of public transport demand, travel patterns and fare compliance.




## Business Objectives

- Analyse passenger journey patterns across Dublin's public transport network.
- Examine transport demand by route, mode and time period.
- Explore passenger categories, payment methods and fare-compliance patterns.
- Identify frequently used origin-destination combinations.
- Build interactive Power BI dashboards for communicating transport insights.
- Demonstrate data engineering, data quality assurance and automated testing practices.

## Data Sources

**NTA GTFS Data:** Public transport reference data covering routes, stops, agencies, trips and service schedules.

**Synthetic Passenger Journey Data:** Artificially generated passenger records used to simulate journey demand, payment methods, passenger categories and fare-compliance outcomes.

The synthetic records are not actual passenger observations, ticketing transactions or operational data supplied by Tracsis or transport operators.


## Technology Stack

| Technology | Purpose |
|---|---|
| Python | GTFS processing, data preparation and synthetic passenger journey generation |
| Pandas | Data cleaning, transformation and validation |
| Databricks | Data ingestion, transformation and analytical table creation |
| SQL | Data querying, aggregation and transport analytics |
| Power BI | Interactive dashboards and data visualisation |
| Pytest | Automated data quality and processing tests |
| Git & GitHub | Version control and project documentation |
| GitHub Actions | Continuous integration and automated testing |

## Data Pipeline Architecture

The project follows a structured data processing workflow:

1. **Data Acquisition:** Obtain publicly available NTA GTFS reference datasets.
2. **Data Preparation:** Use Python to profile the GTFS data and create a Dublin-focused transport network subset.
3. **Synthetic Data Generation:** Generate simulated passenger journeys using the processed transport network.
4. **Data Transformation:** Use Databricks notebooks to process and transform the datasets.
5. **Analytical Modelling:** Produce gold-layer datasets containing passenger journey records and aggregated transport metrics.
6. **Data Visualisation:** Connect the analytical outputs to Power BI for dashboard development.
7. **Quality Assurance:** Validate data processing and synthetic journey logic using automated Python tests.
8. **Continuous Integration:** Run the automated test suite through GitHub Actions when code is pushed or pull requests are created.

## Analytical Outputs

The pipeline produces gold-layer datasets supporting analysis of:

- Daily passenger journey volumes
- Hourly transport demand
- Origin-destination journey patterns
- Passenger categories
- Payment methods
- Route-level journey activity
- Time-period demand
- Transport mode distribution

These analytical outputs are based on synthetic passenger journey data and should not be interpreted as actual observed passenger demand in Dublin.


## Power BI Dashboard

### Transport Overview

![Dublin Transport Overview Dashboard](dashboards/screenshots/Transport_Overview.png)

### Fare Compliance Analysis

![Dublin Fare Compliance Analysis Dashboard](dashboards/screenshots/Fare_Compliance_Analysis.png)


An interactive Power BI report was developed to explore Dublin public transport demand and passenger journey patterns.

The dashboard uses analytical datasets generated through the project's data processing pipeline.

**Power BI Report:**

[View Dublin Transport Analytics Dashboard](https://app.powerbi.com/groups/me/reports/bf99becc-ee45-4d15-9dd9-9dc4119fce39)

The report supports exploration of:

- Passenger journey volumes
- Transport mode distribution
- Route-level demand
- Hourly and daily journey patterns
- Origin-destination analysis
- Passenger categories and payment methods

**Note:** The report uses synthetic passenger journey data. The Power BI link may require authorised access to the report workspace.

## Automated Testing and Data Quality

The project uses Pytest to validate data processing, synthetic journey generation and data quality rules.

The automated test suite covers:

- Passenger attribute validation
- Missing and invalid data detection
- Fare value and compliance consistency
- GTFS stop identification
- Transport network integrity
- Journey stop sequence validation
- Reproducibility of synthetic passenger attributes
- Duplicate journey identifier detection

### Test Results

The test suite contains 18 automated tests.

**Latest verified results:**

- Local execution: 18 passed
- GitHub Actions execution: 18 passed
- Failed tests: 0

Run the tests locally using:

```bash
python -m pytest tests/ -v
```

## Continuous Integration

GitHub Actions automatically executes the Python test suite when changes are pushed to the repository or submitted through pull requests.

The workflow:

1. Checks out the repository.
2. Configures the Python environment.
3. Installs project dependencies.
4. Executes the automated tests using Pytest.
5. Reports the results through GitHub Actions.

The workflow configuration is available at:

`.github/workflows/python-tests.yml`

[View GitHub Actions](https://github.com/prinzy1999/dublin-transport-analytics/actions)

The latest verified workflow completed successfully with all 18 tests passing.


## Repository Structure

```text
dublin-transport-analytics/
|
|-- .github/
|   |-- workflows/
|       |-- python-tests.yml
|
|-- dashboards/
|   |-- power_bi/
|
|-- data/
|   |-- gtfs/
|   |-- processed/dublin/
|   |-- synthetic/
|   |-- exports/gold/
|
|-- databricks/
|-- docs/
|-- src/
|   |-- processing/
|   |-- profiling/
|   |-- synthetic/
|
|-- tests/
|   |-- test_gtfs_processing.py
|   |-- test_synthetic_journeys.py
|   |-- test_data_quality.py
|
|-- .env.example
|-- .gitignore
|-- LICENSE
|-- pyproject.toml
|-- README.md
```

Some directories contain additional files, while empty directories may not appear on GitHub.

## Installation and Testing

### Requirements

- Python 3.10 or later
- Git
- A compatible Python environment
- Databricks access for running cloud notebooks
- Power BI Desktop for opening the report file

### Clone the Repository

```bash
git clone https://github.com/prinzy1999/dublin-transport-analytics.git
cd dublin-transport-analytics
```

### Install Python Dependencies

```bash
python -m pip install -e ".[dev]"
```

### Run Automated Tests

```bash
python -m pytest tests/ -v
```

The automated tests use small sample datasets and do not require the complete NTA GTFS feed.

## Data Availability and Reproducibility

The repository contains Python processing scripts, synthetic passenger journey data, selected analytical exports, Databricks notebooks and a Power BI report.

Some large GTFS source and processed files are excluded from GitHub because of their size.

The original GTFS feed must be obtained separately from an authorised public source and placed in the appropriate local directory before attempting to reproduce the full data pipeline.

The Python tests can be run independently of these large datasets.

Reproducing the complete Databricks workflow requires an appropriately configured Databricks environment and the relevant source datasets.

## Project Limitations

- Passenger journey records are synthetically generated.
- Fare amounts, validation outcomes and compliance classifications are simulated.
- Compliance rates do not represent actual fare compliance in Dublin.
- Journey volumes do not represent observed passenger demand.
- Synthetic passenger behaviour may not reflect real-world transport patterns.
- The analysis is limited by the coverage and structure of the selected GTFS feed.
- Some large source datasets are excluded from the GitHub repository.
- Power BI Service access may require appropriate permissions.

## Data Ethics and Privacy

This project uses publicly available transport reference information and synthetic passenger journey records.

No real passenger identities, individual travel histories or confidential Tracsis operational records are used.

The project is intended for educational and portfolio demonstration purposes.

## Author

Princewill Madugba

Data Analytics Portfolio

[GitHub Profile](https://github.com/prinzy1999)
```
