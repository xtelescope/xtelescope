# coding: utf-8
import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))

import astropy.coordinates
import astropy
import time
coordinate_altay = astropy.coordinates.EarthLocation.from_geodetic(88.31239, 47.7829, 815)

t = astropy.time.Time(time.time(), format="unix")

print(astropy.coordinates.get_moon(t, location=coordinate_altay))
