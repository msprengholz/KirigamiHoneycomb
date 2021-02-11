# write implemenation akin to paper
import numpy as np
import matplotlib.pyplot as plt

# geometry, all in mm
cs = 20 # honeycomb cell size
c_gap = cs / (2*np.cos(np.pi/6)) # gap lenght betwenn folding lines in l direction
xl = 50 # width of panel perpendical to folding direction/ later defined by geometry

# define lower and upper bound fucntion
ld = 0 # lower domain boundary
ud = 200 # upper domain boundary

N = (ud-ld) / cs

ub = lambda x: 0.002*x**2-0.4*x+40 #0.002*x**2-0.2*x+40 #0*x # straight line
lb = lambda x: 10*np.sin(2*np.pi*x/200) #0.01*-((x-100)**2)+150  # inverse parabola

# piecewise linear interpolation
xlp = np.arange(ld, ud+cs/2, cs/2) # sample in half cell width steps, increase ud by cs to get end point in xlp
#print(xlp.size) #should be one more than there are half cells
#print(xlp)

# y interpolation points
ylp_l = lb(xlp)
ylp_u = ub(xlp)
# linear approximation at double the step size to ensure always foldable cross sections!
for i in range(1,xlp.size-1,2):
    ylp_u[i] = (ylp_u[i-1] + ylp_u[i+1]) / 2
for i in range(2,xlp.size-1,2):
    ylp_l[i] = (ylp_l[i-1] + ylp_l[i+1]) / 2


# modify for lower and upper boundary
#ylp_l[1] = lb(xlp[1]) # double precision for first part in lower section
#ylp_u[-2] = ub(xlp[-2]) # double precision for last honeycomb in upper section 

#print(ylp_u)
#print(ylp_l)
# stick to notation in paper
t = ylp_u
u = ylp_l

# create fld
# there are two kinds of vertexes: a and b, they describe the position of slits in length direction (w)
# the slits compromised of a and b take turns along w direction
# they come in pairs of three then they repeat some position down w, e.g. a0,a1,a2 then b0.b1.b2 then a0_1, a1_1, a2_1 and so on

# create data structures
# how many vertexes do we need to save?
a_l = xlp.size 
b0 = np.zeros((a_l, ))
a0 = np.zeros((a_l+1, ))

# num of iterations (based on half cells)
num = a_l
print(num)
# fill them with code from paper
#for m in range(0,num):
#    for i in range(0,m):
#        a0[m] = a0[m-1] + (2*t[2*i+1] - u[2*i] - u[2*i+2]) 
#for m in range(0,num):
#    for i in range(0,m):
#        a1[m] += (2*t[2*i+1] - 2*u[2*i+2])
#    a1[m] = a1[m] -u[0] + t[2*m]
#
#for m in range(0,num):
#    for i in range(0,m):
#        a2[m] = a2[m] + (2*t[2*i+1] - 2*u[2*i+2])
#    a2[m] = a2[m] - u[0] - u[2*m] + 2*t[2*m+1]
#
## b
#for m in range(0,num-1):
#    for i in range(0,m):
#        b0[m] = b0[m] + (2*t[2*i+1] - 2*u[2*i+2]) 
#    b0[m] = b0[m] -u[0] + u[2*m+1]
#for m in range(0,num-1):
#    for i in range(0,m):
#        b1[m] += (2*t[2*i+1] - 2*u[2*i+2])
#    b1[m] = b1[m] -u[0] + t[2*m+1]

# my own implementation!, works as expected
# only if beforehand linear approximation was used (slit width zero)
# a hsa one more as it marks both start and end point
# check: needs to have highest and lowest number!
for i in range(1,num+1):
    # check for uneven i
    if i%2 == 0:
        k = i
    else:
        k = i-1
    a0[i] = a0[i-1] + (t[k] - u[k])
for i in range(1,num):
    if i%2 == 0:
        k = i-1
    else:
        k = i
    b0[i] = b0[i-1] + (t[k] - u[k])
# update start offset for b
b0 = b0  + (u[1]-u[0])


print(a0)
print(b0)


# plotting
x = np.linspace(0,200,100)
y = ub(x)
plt.plot(x,y)
plt.plot(x,lb(x))
plt.plot(xlp, ylp_u, '-o')
plt.plot(xlp, ylp_l, '-o')
#plt.show()





