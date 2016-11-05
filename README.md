# aosss

Adaptive Optics Systems Simulation Support 

Welcome!

# Table of contents

  1. [Introduction](#S1)
  2. [Installation](#S2)
  3. [Usage Examples](#S3)


#<a name=S1></a>1 Introduction

`aosss` is a Python package developed to facilitate E-ELT-MOSAIC star spectroscopy simulations.
These simulations are carried out using WebSim-Compass (http://websim-compass.obspm.fr/) and 
`aosss` can be used to perform (before/after)-the-simulation tasks, such as:

  - assemble a data cube for IFU simulation
  - batch-download simulations resulting files
  - organize resulting files
  - generate visual reports
  - compile results into **spectrum list files**
  - process/convert/visualize these **spectrum list files** 
  
If you have issues, suggestions, requests or would like to collaborate in this project,
please send a message to juliotrevisan@gmail.com

#<a name=S2></a>1.1 Structure

`aosss` contains an API (application programming interface) and a set of scripts (standalone programs)
that use this API.

## Programs available

:bulb: To print a list of `aosss` programs, run `aosss-programs.py` from the console.
As of today (5th/Nov/2016, it will give you the following output)

Graphical applications:
  - `aosss-wavelength-chart.py` -- Draws a [wavelength] x [various stacked information] chart

Command-line tools:
  - `aosss-create-spectrum-lists.py` -- Create several .splist files, grouping spectra by their wavelength vector
  - `aosss-create-websim-report.py` -- Creates report for a given set of WEBSIM-COMPASS output files
  - `aosss-get-compass.py` -- Downloads a number of Websim-Compass simulations
  - `aosss-programs.py` -- Lists all programs available with `aosss` package

All the programs above can be called with the `--help` or `-h` option for more documentation

#<a name=S1></a>2 Installation

# 2.0 Requirements

  - Python 3
  - `pyfant` (another Python package) (see below)

**Note** Although it can run on any OS platform, the following instructions 
target Debian-based Linux users (such as Ubuntu).

# 2.1 Install `pyfant` package
 
 Follow the link to http://github.com/trevisanj/pyfant and follow installation instructions
   
# 2.2 Clone this repository

```shell
git clone https://github.com/trevisanj/aosss
```

# 2.3 Run Python installation script

```shell
sudo python setup.py develop
```

## 1.1 Installing updates

:one: Pull updates from from GitHub:

```shell
cd <aosss folder>
git pull
```

:two: Run `setup.py` again: `sudo python setup.py develop`

#<a name=S3></a>3. Usage Examples

