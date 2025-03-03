# LE completeness analysis

This project is used to analyse the completness of LE interval data for a device, a range of devices or a fleet.

# Prerequisites
- [pyenv](https://github.com/pyenv/pyenv)
- [poetry](https://python-poetry.org/) 

# Install

- Clone the repo
- In your terminal execute 
```Shell
cd le_completeness_analysis
pyenv local 3.12
poetry env use 3.12
poetry install
```

# App configuration

The app is configured through a `.env` file.

To set this up, copy `example.env` and rename it to `.env`. Then define the config variables.


## Analyse data

In your terminal execute:

```Shell
cd le_completeness_analysis/le_completeness_analysis
poetry shell
jupyter notebook
```

This will open the Jupyter notebook interface in your web browser.
From here, open `analysis.ipynb`

Follow the instructions in the `Device id(s) configuration`, `Period configuration`, and `Threshold configuration` cells.

Execute all cells in the notebook. This may take a while depending on the amount of data that needs to be downloaded.

Scroll to the `Outputs` section of the notebook, where you will find analysis results at different levels of detail. (top level stats, per device stats for the whole period, per device stats per day, and the raw interval data). Data is presented in tables that can be sorted, filtered and exported.

# Notes

Jupyter notebook files can get very large when they have output in them. When making PRs against this repo, please first clear all output from the notebook.