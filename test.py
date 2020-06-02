from ncempy.io import dm; import matplotlib.pyplot as plt; import time
dmData = dm.dmReader('./Data/example.dm3') #a simple one image data file
plt.imshow(dmData['data']) #show the image using pyplot
plt.show()