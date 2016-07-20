from pyfant import *
from fileccube import *

fsp = load_spectrum("flux.spec")
ccube = CompassCube()
ccube.create0(ifu_width=5, ifu_height=3, x=10, y=10, sp=fsp.spectrum)
ccube.paint(0, 0, fsp.spectrum)  # paints lower left corner

fcube = FileCCube()
fcube.ccube = ccube
fcube.save_as("eheh.fits")