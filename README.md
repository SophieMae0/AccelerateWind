# AccelerateWind

This repository is created to determine a cost effective way to optimize wind turbine parts for Accelerate Wind turbines. The turbines will be located at around 10 meters high and will include a fly wheel so the data used must be taken at least every 5 minutes. Data that meets these requirements was not available online so it was generated based on data that was available.

Data taken every 5 minutes at 100 meters was downloaded from https://cds.climate.copernicus.eu/#!/home. 3 years of data was downloaded over coordinates spanning a rectangle that covers the USA (25 to 50, 55 to 114). There were about 1000 sites chosen equally dispersed throughout the USA. fiveMinutes.py can be run once this data is downloaded to combine data for each coordinant. The names of the cleaned files are the site coordinants

Data taken once an hour at 10 meters was downloaded from https://github.com/NREL/hsds-examples/blob/master/README.md with the hourly.py script. This script downloads data for each site where 100 meter data was previosly downloaded. 

Once data is downloaded prediction.py uses both sets to run polynomial regression and generate 10 meter data taken every 5 minutes.

dump.py analzyes the data and pickles specific information based on the predicted 10 meter 5 minute data. The main 4 function are:

dump_pickles_one_gen - calulates optimal generator size

dump_pickles_one_fly - annual energy produced with and without a flywheel

dump_pickles_basic - speed, velocity, pwer, energy, angle of wind

dump_pickles_cost - generator and flywheel combination that have the lowest cost

load.py generates maps of the USA with information about wind turbine (such as angle of highest efficiency, most effiecient generator and flywheel size, etc) based on the data that was pickled in dump. The main 4 functions are:

load_graphs_one_gen - calulates ptimal generator size

load_graphs_one_fly - calulates annual energy produced with and without a flywheel

load_graphs_basic - calulates speed, velocity, pwer, energy, angle of wind

load_graphs_cost - calulates generator and flywheel combination that have the lowest cost
