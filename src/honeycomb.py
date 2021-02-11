import numpy as np
import matplotlib.pyplot as plt
# geometry, all in mm
cs = 20 # honeycomb cell size in w direction
c_gap = cs / (2*np.cos(np.pi/6)) # gap lenght betwenn folding lines in l direction
#print(c_gap)
xl = 100 # width of panel perpendical to folding direction/ later defined by geometry

# define lower and upper bound fucntion
ld = 0 # lower domain boundary
ud = 200 # upper domain boundary
xw = ud-ld # width of panel in folding line direction

Nw = xw / cs 
Nl = int(xl // c_gap) # number of folding lines in l direction

# compute honeycomb pattern
hs_l = cs / 2 # honeycomb pattern step size
hs_w = cs / np.sqrt(3) # honeycomb pattern step size

L = hs_w
print(L)

max_l = int(np.floor(xl / hs_l))+1 # ensure to always be greater than the given lengths in w and l
max_w = int(np.floor(xw / hs_w))+1 

#ny = np.arange(0, max_l) * hs_l
#ny = np.tile(ny, max_w) # repeat 
#ny.shape = (max_w, max_l) # convert to 2D

ratio = np.sqrt(3)/2
# create double size traingular grid pattern
nx, ny = np.meshgrid(np.arange(xw//(L*np.sqrt(3))), np.arange(xl//(3*L)), indexing='xy')
nx = nx.astype(np.float64)
ny = ny.astype(np.float64)
ny[0::2, :] += 3/2*L
#nx *= cs
#ny *= ratio*cs
nx = nx.flatten()
ny = ny.flatten()

print(ny)



# create oversize array for honeycomb vertices
#nx = np.zeros((max_l*max_w))
#ny = np.zeros((max_l*max_w))


plt.plot(nx, ny, 'o')
plt.axis('scaled')
plt.show()
