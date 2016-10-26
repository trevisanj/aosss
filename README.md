# oasis
Adaptive Optics Systems Simulation Support 

Welcome!

#<a name=S1></a>1 Installation

:one: Install _pyfant_ package from http://github.com/trevisanj/pyfant
   
:two: Clone this repository: `git clone https://github.com/trevisanj/aosss`

:three: Run `sudo python setup.py develop`

## 1.1 Installing updates

:one: Pull updates from from GitHub:

```shell
cd <ao3s folder>
git pull
```

:two: Run `setup.py` again: `sudo python setup.py develop`

#<a name=S2></a>2 Programs Available

:bulb: To print a list of all command-line tools, run `aosss-programs.py`

Graphical applications:
  - `aosss-wavelength-chart.py` -- Draws a [wavelength] x [various stacked information] chart

Command-line tools:
  - `aosss-create-spectrum-lists.py` -- Create several .splist files, grouping spectra by their wavelength vector
  - `aosss-create-websim-report.py` -- Creates report for a given set of WEBSIM-COMPASS output files
  - `aosss-get-compass.py` -- Downloads a number of Websim-Compass simulations
  - `aosss-programs.py` -- Lists all programs available with `aosss` package

