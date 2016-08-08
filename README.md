# pymos

## Installation

:one: Install the _pyfant_ package following instructions at http://github.com/trevisanj/PFANT. Within these instructions, please:

  - choose to clone the _PFANT_ repository (don't download zip file, as the _PFANT_ project is constantly being updated to fulfill needs of the _pymos_ project, and you may eventually need to `git pull` the _PFANT_ repository)
  - there is no need to compile the Fortran code for the sake of pymos
    
:two: Clone the _pymos_ repository: `git clone https://github.com/trevisanj/pymos`

:three: Run `add-paths.py` in _bash_ or _tcsh_ mode (similar to step in PFANT installation)

:four: Testing

  - Create any working directory of your choice. This will be used to work with your data files
  - From there, type `skyed.py`
  - Press `Ctrl+D` to create new data cube
  - You can now start adding spectra to the cube
