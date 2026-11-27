# LE completeness analysis

This project is used to analyse the completeness of LE interval data for a device, a range of devices, or a fleet.

The main notebook for local use is `le_completeness_analysis/analysis_colab_daily_completeness.ipynb`.

## Local setup

These steps assume your colleagues are working on macOS and have downloaded the repository as a zip file from GitHub.

1. Unzip the repository and open a terminal in the project root.
2. Install Homebrew if it is not already installed:

	```bash
	/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	```

3. Install Python 3.12:

	```bash
	brew install python@3.12
	```

4. Create and activate a local virtual environment:

	```bash
	python3.12 -m venv .venv
	source .venv/bin/activate
	```

5. Install the notebook dependencies:

	```bash
	python -m pip install --upgrade pip
	pip install pandas notebook python-dotenv pendulum plotly itables httpx ipykernel
	python -m ipykernel install --user --name le-completeness-analysis --display-name "LE Completeness Analysis"
	```

## Add credentials

Credentials are read from a `.env` file in the project root (it is gitignored, so it is never committed). Copy the template and fill in the values:

```bash
cp example.env .env
```

- `API_KEY`: Public REST API key
- `UA_USERNAME`: User Apps username
- `UA_PASSWORD`: User Apps password

The notebook stops with an error if `API_KEY` is missing, and the UA credentials are required for the decommissioned-device checks.

To choose which devices are analysed, edit `DEVICE_IDS` in the first configuration code cell of the notebook.
If you want to analyse all devices available to the API key, leave `DEVICE_IDS` as an empty list.
If you want to analyse a subset of devices, add the device ids to `DEVICE_IDS`.

## Run the notebook

1. Start Jupyter from the project root:

	```bash
	jupyter notebook
	```

2. Open `le_completeness_analysis/analysis_colab_daily_completeness.ipynb`.
3. Select the `LE Completeness Analysis` kernel if prompted.
4. Update the values in the `Device id(s) configuration`, `Period configuration`, `Threshold configuration`, and `Other config` cells.
5. Run all cells.

Execution may take a while, especially for large device sets or long date ranges.

## Re-running the notebook

Before re-running the analysis, delete the old notebook file that contains the previous results and reopen a fresh copy of `le_completeness_analysis/analysis_colab_daily_completeness.ipynb`. This avoids confusion caused by stale outputs from an earlier run.

## Data cache

The notebook caches each device's daily results in `le_completeness_analysis/data/` (one CSV per device, plus device names, first-heard timestamps, and decommissioned/uninitialised device lists). Re-runs only download days that aren't cached yet, which makes them much faster. Days that are still in progress, or that a device hasn't uploaded data for yet, are not cached, so they are downloaded again on the next run.

The cache is local to your machine and is not committed to git. Delete the folder to force a full re-download.

## Output

Scroll to the `Outputs` section of the notebook for the analysis results. The notebook produces top-level stats, per-device stats for the whole period, per-device stats per day, and raw interval data. Tables can be sorted, filtered, and exported.