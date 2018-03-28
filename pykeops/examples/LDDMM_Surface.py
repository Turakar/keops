#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example of diffeomorphic matching of surfaces using varifolds metrics
We perform LDDMM matching of two meshes using the geodesic shooting algorithm
expected times of computation with default settings : 
    on Cpu (small size example)  : 11 s
    on Gpu (medium size example) : 27 s
"""

import os.path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + (os.path.sep + '..')*2)

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import torch
from torch.autograd import Variable, grad

import time

from pykeops.torch.kernels import Kernel, kernel_product

use_cuda = torch.cuda.is_available()
backend_keops = "GPU_1D_device" if use_cuda else "GPU_1D_host"
print("backend for keops is set to :", backend_keops)

###### main settings for this example ############################
kernel_lib = "keops"     # "pytorch" or "keops"
deviceId = 0             # id of Gpu device (in case Gpu is  used)
# data file : one of :
#   "hippos.pt" : original data (6611 vertices), 
#   "hippos_red.pt" : reduced size (1654 vertices), 
#   "hippos_reduc.pt" : further reduced (662 vertices), 
#   "hippos_reduc_reduc.pt" : further reduced (68 vertices)
if use_cuda:
    datafile = 'data/hippos_reduc.pt'
else:
    datafile = 'data/hippos_reduc_reduc.pt'
##################################################################


# function to transfer data on Gpu only if we use the Gpu
def CpuOrGpu(x):
    if use_cuda:
        if type(x)==tuple:
            x = tuple(map(lambda x:x.cuda(),x))
        else:
            x = x.cuda()
    return x


# define Gaussian kernel (K(x,y)b)_i = sum_j exp(-|xi-yj|^2)bj
def GaussKernel(sigma,lib="keops"):
    if lib=="pytorch":
        oos2 = 1/sigma**2
        def K(x,y,b):
            return torch.exp(-oos2*torch.sum((x[:,None,:]-y[None,:,:])**2,dim=2))@b
        return K
    elif lib=="keops":
        def K(x,y,b):
            params = {
                "id"      : Kernel("gaussian(x,y)"),
                "gamma"   : Variable(CpuOrGpu(torch.FloatTensor([1/sigma**2]))),
                "backend" : backend_keops
            }
            return kernel_product( x,y,b, params)
        return K

# define "Gaussian-CauchyBinet" kernel (K(x,y,u,v)b)_i = sum_j exp(-|xi-yj|^2) <ui,vj>^2 bj
def GaussLinKernel(sigma,lib="keops"):
    if lib=="pytorch":
        oos2 = 1/sigma**2
        def K(x,y,u,v,b):
            Kxy = torch.exp(-oos2*torch.sum((x[:,None,:]-y[None,:,:])**2,dim=2))
            Sxy = torch.sum(u[:,None,:]*v[None,:,:],dim=2)**2
            return (Kxy*Sxy)@b
        return K
    elif lib=="keops":
        def K(x,y,u,v,b):
            params = {
                "id"      : Kernel("gaussian(x,y) * linear(u,v)**2"),
                "gamma"   : (Variable(CpuOrGpu(torch.FloatTensor([1/sigma**2]))),Variable(CpuOrGpu(torch.FloatTensor([0])))),
                "backend" : "auto"
            }
            return kernel_product( (x,u),(y,v),b, params)
        return K

# custom ODE solver, for ODE systems which are defined on tuples
def RalstonIntegrator(nt=10):
    def f(ODESystem,x0,deltat=1.0):
        x = tuple(map(lambda x:x.clone(),x0))
        dt = deltat/nt
        for i in range(nt):
            xdot = ODESystem(*x)
            xi = tuple(map(lambda x,xdot:x+(2*dt/3)*xdot,x,xdot))
            xdoti = ODESystem(*xi)
            x = tuple(map(lambda x,xdot,xdoti:x+(.25*dt)*(xdot+3*xdoti),x,xdot,xdoti))
        return x
    return f

# LDDMM implementation
def Hamiltonian(K):
    def H(p,q):
        return .5*(p*K(q,q,p)).sum()
    return H

def HamiltonianSystem(K):
    H = Hamiltonian(K)
    def HS(p,q):
        Gp,Gq = grad(H(p,q),(p,q), create_graph=True)
        return -Gq,Gp
    return HS

def Shooting(p0,q0,K,deltat=1.0,Integrator=RalstonIntegrator()):
    return Integrator(HamiltonianSystem(K),(p0,q0),deltat)

def Flow(x0,p0,q0,K,deltat=1.0,Integrator=RalstonIntegrator()):
    HS = HamiltonianSystem(K)
    def FlowEq(x,p,q):
        return (K(x,q,p),)+HS(p,q)
    return Integrator(FlowEq,(x0,p0,q0),deltat)[0]

def LDDMMloss(K,dataloss,gamma=0):
    def loss(p0,q0):
        p,q = Shooting(p0,q0,K)
        return gamma * Hamiltonian(K)(p0,q0) + dataloss(q)
    return loss

# Varifold data attachment loss for surfaces
# VT: vertices coordinates of target surface, 
# FS,FT : Face connectivity of source and target surfaces
# K kernel
def lossVarifoldSurf(FS,VT,FT,K):
    def CompCLNn(F,V):
        V0, V1, V2 = V.index_select(0,F[:,0]), V.index_select(0,F[:,1]), V.index_select(0,F[:,2])
        C, N = .5*(V0+V1+V2), .5*torch.cross(V1-V0,V2-V0)
        L = (N**2).sum(dim=1)[:,None].sqrt()
        return C,L,N/L
    CT,LT,NTn = CompCLNn(FT,VT)
    cst = (LT*K(CT,CT,NTn,NTn,LT)).sum()
    def loss(VS):
        CS,LS,NSn = CompCLNn(FS,VS)
        return cst + (LS*K(CS,CS,NSn,NSn,LS)).sum() - 2*(LS*K(CS,CT,NSn,NTn,LT)).sum()
    return loss


def RunExample(datafile=datafile,kernel_lib="keops"):
    # load dataset
    VS,FS,VT,FT = CpuOrGpu(torch.load(datafile))
    q0 = VS = Variable(VS,requires_grad=True)
    VT, FS, FT = Variable(VT), Variable(FS), Variable(FT)

    # define data attachment and LDDMM functional
    dataloss = lossVarifoldSurf(FS,VT,FT,GaussLinKernel(sigma=20,lib=kernel_lib))
    Kv = GaussKernel(sigma=20,lib=kernel_lib)
    loss = LDDMMloss(Kv,dataloss)

    # initialize momentum vectors
    p0 = Variable(CpuOrGpu(torch.zeros(q0.shape)), requires_grad=True)

    # perform optimization
    optimizer = torch.optim.LBFGS([p0])
    N = 5
    print('performing optimization...')
    start = time.time()
    for i in range(N):
        def closure():
            optimizer.zero_grad()
            L = loss(p0,q0)
            L.backward()
            return L
        optimizer.step(closure)
    print('Optimization time : ',round(time.time()-start,2),' seconds')

    # display output    
    fig = plt.figure();
    plt.title('LDDMM matching example')  
    p,q = Shooting(p0,q0,Kv)
    q0np, qnp, FSnp = q0.data.cpu().numpy(), q.data.cpu().numpy(), FS.data.cpu().numpy()
    VTnp, FTnp = VT.data.cpu().numpy(), FT.data.cpu().numpy()    
    ax = Axes3D(fig)
    ax.axis('equal')
    ax.plot_trisurf(q0np[:,0],q0np[:,1],q0np[:,2],triangles=FSnp,alpha=.5)
    ax.plot_trisurf(qnp[:,0],qnp[:,1],qnp[:,2],triangles=FSnp,alpha=.5)
    ax.plot_trisurf(VTnp[:,0],VTnp[:,1],VTnp[:,2],triangles=FTnp,alpha=.5)

# run the example
if use_cuda:
    with torch.cuda.device(deviceId):
        RunExample(datafile,kernel_lib)
else:
    RunExample(datafile,kernel_lib)

print("Done.")
plt.show(block=True)

