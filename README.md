# LE completeness analysis

This project is used to analyse the completness of LE interval data for a device, a range of devices or a fleet.

The project contains a single notebook, `analysis_colab.ipynb`.
Open the file in the Github browser and click the "Open in Colab" button at the top of the document.

This will open the Jupyter notebook interface in the Google Colab environment.

Follow the instructions in the `Device id(s) configuration`, `Period configuration`, `Threshold configuration` and `Other config` cells.

By default the notebook only analyses LE interval data aggregated into daily granularity. If you want the notebook to output per device analysis at the 5 minute interval granularity, set the `ANALYSE_UNAGGREGATED_DATA` constant to `True` (and ensure you analyse a maximum of 30 devices). The notebook will then also output missing interval graphs on a per device basis (both as a time series graph and as a time-of-day graph).

Execute all cells in the notebook by selecting `Runtime/Run All` from the top menu. Execution may take a while (can take hours) depending on the amount of data that needs to be downloaded.

Scroll to the `Outputs` section of the notebook, where you will find analysis results at different levels of detail. (top level stats, per device stats for the whole period, per device stats per day, and the raw interval data). Data is presented in tables that can be sorted, filtered and exported.