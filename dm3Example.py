#For DM3
import DM3lib as dm3
import matplotlib.pyplot as plt
import os.path
from PIL import Image
import numpy as np

# This loads all of the data from hte dm3 file
dm3f = dm3.DM3("example.dm3")
print dm3f.tags
print "pixel size = %s %s"%dm3f.pxsize

p = plt.matshow(dm3f.imagedata[0])
#p = plt.plot([1, 23, 2, 4])
plt.axis('off')
plt.show()

# - save as PNG and JPG
#for i in range()
#im_dsp = Image.fromarray(dm3f.imagedata[0])
#im_dsp.save(os.path.join("save.png"))