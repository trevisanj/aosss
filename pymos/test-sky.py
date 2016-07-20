from pyfant import *

from fileccube import *
from filesky import *

fc = FileCCube()
fc.load("eheh.fits")

fsky = FileSky()
fsky.sky.from_compass_cube(fc.ccube)
fsky.save_as(FileSky.default_filename)