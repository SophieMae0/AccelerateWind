# AccelerateWind

This repository is created to determine a cost effective way to optimize wind turbine parts for Accelerate Wind turbines. The turbines will be located at around 10 meters high and will include a fly wheel so the data used must be taken at least every 5 minutes. Data that meets these requirements was not available online so it was generated based on data that was available.

Data taken every 5 minutes at 100 meters was downloaded from https://cds.climate.copernicus.eu/#!/home. 3 years of data was downloaded over coordinates spanning a rectangle that covers the USA (25 to 50, 55 to 114). There were about 1000 sites chosen equally dispersed throughout the USA. fiveMinutes.py can be run once this data is downloaded to combine data for each coordinant. The names of the cleaned files are the site coordinants

Data taken once an hour at 10 meters was downloaded from https://github.com/NREL/hsds-examples/blob/master/README.md with the hourly.py script. This script downloads data for each site where 100 meter data was previosly downloaded. 

Once data is downloaded prediction.py uses both sets to run polynomial regression and generate 10 meter data taken every 5 minutes.

wind_data_analysis.py generates maps of the USA with information about wind turbine efficiency at 10 meters (such as angle of highest efficiency, most effiecient generator and flywheel size, etc)
