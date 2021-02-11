import trimesh
import svgwrite
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

#print(ylp_u)
#print(ylp_l)
# stick to notation in paper
t = ylp_u
u = ylp_l

# create fld
# there are two kinds of vertexes: a and b, they describe the position of slits in length direction (w)
# the slits comprised of a and b take turns along w direction

# create data structures
# how many vertexes do we need to save?
# num of iterations (based on half cells)
num = xlp.size 
#print(xlp)
#print(num)
a0 = np.zeros((num+1, ))
b0 = np.zeros((num, ))

# FLD code
# my own implementation!, works as expected
# only if beforehand linear approximation was used (slit width zero)
# a has one more as it marks both start and end point
# check: needs to have highest and lowest number!

# the counting range changes depending on what cells are the end of the sequence...
if num%2 == 0:
    c_num = num
else:
    c_num = num+1

for i in range(1,c_num):
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
# plot / compute vertex positions 
vx = np.zeros((Nl*num), ) # FLD x coordinates
vy = np.zeros((Nl*num), ) # FLD x coordinates
c_offset = 0 # depending on where in pattern we start to count

for i in range(num):
    for k in range(Nl):
        #print(i,k)
        m = (k+c_offset) % 4
        if m==0:
            vx[i*Nl+k] = a0[i]
        elif m==1:
            vx[i*Nl+k] = a0[i]
        elif m==2:
            vx[i*Nl+k] = b0[i]
        elif m==3:
            vx[i*Nl+k] = b0[i]
        vy[i*Nl+k] = k * c_gap

#print(vx, vy)

# compute honeycomb pattern
hs_w = cs / 2 # honeycomb pattern step size
hs_l = cs / np.sqrt(3) # honeycomb pattern step size
# number of steps in each direction
hx_m = int(np.ceil(xw / hs_w + 1)) # make pattern definetly fill area (ceil), can be tuned later
hy_m = int(np.ceil(xl / hs_l + 1)) 
# coordinate storage arrays
hx = []#np.zeros((hx_m*hy_m, ))
hy = []#np.zeros((hx_m*hy_m, ))
t3d = [] # create arrays of same length as hx and hy with height values
u3d = []

# compute honeycomb vertices
# pattern is generated from left to right (x direction) and from bottom to top (y-direction)
# TODO: calc subset, then repeat array...
for i in range(hx_m):
    for k in range(hy_m):
        if i%2==0: # even i (x direction)  
            if (k+1)%3>0:
                #hy[i*hy_m+k] = k * hs_l 
                hy.append(k * hs_l)
                #hx[i*hy_m+k] = i * hs_w
                hx.append(i * hs_w)
                t3d.append(t[i])
                u3d.append(u[i])
        else: # uneven i 
            if (k+0)%3>0:
                #hy[i*hy_m+k] = k * hs_l + hs_l/2 # offset of pattern
                hy.append(k * hs_l + hs_l/2)
                #hx[i*hy_m+k] = i * hs_w
                hx.append(i * hs_w)
                t3d.append(t[i])
                u3d.append(u[i])

# count points in line (y direction)
l = 0 # length counter
c_l = 1 # point counter (at 0,0 is the first point, so start with 1)
a_p = 1
b_p = 0
while l<xl:
    if (c_l+c_offset)%4 == 0:
        c_l += 1
        l += hs_l
        a_p += 1
    elif (c_l+c_offset)%4 == 1:
        c_l += 1
        l += hs_l/2
        b_p += 1
    elif (c_l+c_offset)%4 == 2:
        c_l += 1
        l += hs_l
        b_p += 1
    elif (c_l+c_offset)%4 == 3:
        c_l += 1
        l += hs_l/2
        a_p += 1

# array of 2d points
points2d = np.column_stack((hx,hy))
# create array of all points in 3D space, use t and u
p3d_t = np.column_stack((hx,hy,t3d))
p3d_u = np.column_stack((hx,hy,u3d))
# upper then lower points
p3d = np.vstack((p3d_t, p3d_u))
# length of t array part (half of combined array)
lu = p3d_t.shape[0]


# order points for quad generation
# hardcode, calc later
num_b = int(np.floor(hx_m/2))
#print(num_b)

quad_ind = [] # store indices of pts for quad generation, only one half (upper or lower, are the same)

for i in range(num_b):
    # define starting point in p3d array
    stp = c_l * i#(a_p+b_p)*i
    # repeat for left and right a columns
    
    # left
    # for each point in line
    # counter for a and b points
    if False:#((i == num_b-1) and (hx_m%2 == 0)): # pattern becomes non symmetric, last point is cut off!
        c = c_l - 1
    else:
        c = c_l
    a_c = b_c = 0
    for k in range(c):
        sel = k%4
        if sel==0:
            quad_ind.append(stp+a_c)
            a_c += 1
        elif sel==1:
            quad_ind.append(stp+a_c)
            a_c += 1
        elif sel==2:
            quad_ind.append(stp+a_p+b_c)
            b_c += 1
        elif sel==3:
            quad_ind.append(stp+a_p+b_c)
            b_c += 1
    if ((i == num_b-1) and (hx_m%2 == 0)):
        # if on last iteration for b rows (i) and even number of cells, pass
        pass
    else:
        #right
        a_c = b_c = 0
        for k in range(c_l):
            sel = k%4
            if sel==0:
                quad_ind.append(stp+c_l+a_c)
                a_c += 1
            elif sel==1:
                quad_ind.append(stp+c_l+a_c)
                a_c += 1
            elif sel==2:
                quad_ind.append(stp+a_p+b_c)
                b_c += 1
            elif sel==3:
                quad_ind.append(stp+a_p+b_c)
                b_c += 1


# calc number of lines in x direction
num_lines_w = hx_m-1 

# create quad mesh face array
quads = []

for i in range(num_lines_w):
    if False:#((i == num_lines_w-1) and (hx_m%2 == 0)):
        for k in range(c_l-1):
            quads.append([quad_ind[i*c_l+k], quad_ind[i*c_l+k+1], quad_ind[i*c_l+k]+lu, quad_ind[i*c_l+k+1]+lu])
    else:
        for k in range(c_l-1):
            quads.append([quad_ind[i*c_l+k], quad_ind[i*c_l+k+1], quad_ind[i*c_l+k]+lu, quad_ind[i*c_l+k+1]+lu])

#print(quads)

# from quads to tris (with numpy)
quads = np.asarray(quads)
tris = np.empty((quads.shape[0], 2, 3))
tris[:,0,:] = quads[:,(0,1,2)]
tris[:,1,:] = quads[:,(2,3,1)] # update to get face ordering trimesh uses.. enable back face culling
tris.shape = (-1, 3)

# show mesh

mesh = trimesh.Trimesh(vertices=p3d,
                       faces=tris,
                       process=True)

#mesh.show(smooth=False)
mesh.export("hex.stl")

# create svg FLD output file
vx_max = np.amax(vx)
vy_max = np.amax(vy)
# define colors
c_cut = 'black'
c_fold = 'green'
stroke_w = 0.2 # stroke width

dwg = svgwrite.Drawing('fld.svg', profile='tiny', size=(str(vx_max+stroke_w)+'mm', str(vy_max+stroke_w)+'mm'), viewBox=(str(-stroke_w/2)+' '+str(-stroke_w/2)+' ' +str(vx_max+stroke_w)+' '+str(vy_max+stroke_w)))
# DRAW
# folding lines
i = 0
dwg.add(dwg.line((vx[i], i*c_gap), (vx[vx.size-Nl+i], i*c_gap), stroke=c_cut, stroke_width=stroke_w))
i = Nl-1
dwg.add(dwg.line((vx[i], i*c_gap), (vx[vx.size-Nl+i], i*c_gap), stroke=c_cut, stroke_width=stroke_w))
for i in range(1,Nl-1):
        dwg.add(dwg.line((vx[i], i*c_gap), (vx[vx.size-Nl+i], i*c_gap), stroke=c_fold, stroke_width=stroke_w))

# cutting lines in l direction
# first and last line are always cut through
for k in range(Nl-1):
    i = 0
    dwg.add(dwg.line((vx[Nl*i+k], vy[Nl*i+k]), (vx[Nl*i+k+1], vy[Nl*i+k+1]), stroke=c_cut, stroke_width=stroke_w))
    i = num-1
    dwg.add(dwg.line((vx[Nl*i+k], vy[Nl*i+k]), (vx[Nl*i+k+1], vy[Nl*i+k+1]), stroke=c_cut, stroke_width=stroke_w))

for i in range(1, num-1):
    for k in range(Nl-1):
        # every second cut has to be additionally offset by two
        offset = ( (i+1) % 2)*2
        # calc which color to draw
        sel = (k+c_offset+offset)%4
        if sel==0:
            color = c_cut 
        elif sel==1:
            color = c_cut 
        elif sel==2:
            color = c_fold 
        elif sel==3:
            color = c_cut 
        dwg.add(dwg.line((vx[Nl*i+k], vy[Nl*i+k]), (vx[Nl*i+k+1], vy[Nl*i+k+1]), stroke=color, stroke_width=stroke_w))

dwg.save()


# plotting
x = np.linspace(0,200,100)
y = ub(x)
#plt.plot(x,y)
#plt.plot(x,lb(x))
#plt.plot(xlp, ylp_u, '-o')
#plt.plot(xlp, ylp_l, '-o')
#plt.plot(vx, vy, 'o')
#plt.plot(hx, hy, 'o')
plt.axis('scaled')
plt.show()


