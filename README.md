# ao3s
Adaptive Optics Systems Simulation Support 

Welcome!

#<a name=S1></a>1 Installation

:one: Install _pyfant_ package from http://github.com/trevisanj/pyfant
   
:two: Clone this repository: `git clone https://github.com/trevisanj/ao3s`

:three: Run `sudo python setup.py develop`

## 1.1 Installing updates

:one: Pull updates from from GitHub:

```shell
cd <ao3s folder>
git pull
```

:two: Run `setup.py` again: `sudo python setup.py develop`

#<a name=S2></a>2 Programs Available

:bulb: To print a list of all command-line tools, run `ao3s-programs.py`

Graphical applications:
  - `ao3s-wavelength-chart.py` -- Draws a [wavelength] x [various stacked information] chart

Command-line tools:
  - `ao3s-create-spectrum-lists.py` -- Create several .splist files, grouping spectra by their wavelength vector
  - `ao3s-create-websim-report.py` -- Creates report for a given set of WEBSIM-COMPASS output files
  - `ao3s-get-compass.py` -- Downloads a number of Websim-Compass simulations
  - `ao3s-programs.py` -- Lists all programs available with `ao3s` package

