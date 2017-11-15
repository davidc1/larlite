import ROOT
from ROOT import geoalgo
from ROOT import larlite
import numpy as np
import matplotlib.pyplot as plt
import sys, os

#scan_v = [0,4,25,26,29,40,51,52,56,57,63,71,73,78,80,83,84,92,99,103,105,111,114,118,120,137,157,162,168,173,174]
#scan_v = [0,1,5,6,8,10,16,19,24,25,35,45,52,54,59,63,70,71,74,78,87,90,92,99,102,104,105,108,127,134,138,150,157]
scan_v = [0,1,3,4,5,8,10,19,23,24,26,35,41,43,44,49,52,54,59,67,70,71,73,74,78,79,90,92,99,104,105,108,114,120,127,129,138,144,150,157,160,162,174]
#scan_v = [49]
masses = []
radlen = []
impact = []

def RadLen(shr1,vtx):

    strt1 = shr1.ShowerStart()

    A = geoalgo.Vector( strt1.X(), strt1.Y(), strt1.Z() )
    
    rA = A.Dist( vtx )

    return rA

def IPerror(shr1,shr2,vtx):

    A = geoalgo.Vector( shr1.X(), shr1.Y(), shr1.Z() )
    B = geoalgo.Vector( shr2.X(), shr2.Y(), shr2.Z() )
    
    rA = A.SqDist( vtx )
    rB = B.SqDist( vtx )

    # angular uncertainty is 10 degrees
    tan = np.tan( 10 * 3.14 / 180. )

    error = tan * np.sqrt( rA + rB )

    return error

def IP(shr1,shr2,vtx):

    dir1  = shr1.Direction()
    dir1 *= -1
    strt1 = shr1.ShowerStart()
    dir2  = shr2.Direction()
    dir2 *= -1
    strt2 = shr2.ShowerStart()

    s1 = geoalgo.HalfLine()
    s1.Start(strt1)
    s1.Dir(dir1)

    s2 = geoalgo.HalfLine()
    s2.Start(strt2)
    s2.Dir(dir2)

    geoAlgo = geoalgo.GeoAlgo()

    dist = np.sqrt( geoAlgo.SqDist(s1,s2) )

    error = IPerror(strt1,strt2,vtx)

    sigma = dist/error
    
    print 'IP is : %.02f +/- %.02f  -> %.02f sigma from 0'%(dist,error,sigma)
    return dist,sigma

#fin = ROOT.TFile('/home/david/uboone/data/goldenpi0/fordc_novtx_filtered_output_showers.root')
#fin = ROOT.TFile('/home/david/uboone/larlite_showers/UserDev/RecoTool/ShowerReco3D/showerRecoUboone_Angle3DFromVtx.root')
fin = ROOT.TFile('/home/david/uboone/larlite_showers/UserDev/RecoTool/ShowerReco3D/showerRecoUboone.root')

showers = fin.Get('shower_showerreco_tree')
vertex  = fin.Get('vertex_mcvertex_tree')
event = fin.Get('larlite_id_tree')

for n in xrange(showers.GetEntries()):
#for n in scan_v:

    showers.GetEntry(n)
    vertex.GetEntry(n)
    event.GetEntry(n)

    print
    print
    print
    print 'Entry : %i'%n
    print 'RUN   : %i'%event._run_id
    print 'EVENT : %i'%event._event_id
    print

    shower_v = showers.shower_showerreco_branch
    vertex_v = vertex.vertex_mcvertex_branch

    vtx = vertex_v.at(0)

    xyz = geoalgo.Vector(vtx.X(),vtx.Y(),vtx.Z())

    print 'There are %i showers in this event'%(len(shower_v))

    if (len(shower_v) == 2):

        for i in xrange(len(shower_v)):
            for j in xrange(i+1,len(shower_v)):

                print 'comparing showers %i and %i'%(i,j)
                
                ip,sigma = IP( shower_v.at(i), shower_v.at(j), xyz )

                impact.append(ip)

                #if (sigma < 30.0):
                if (ip < 4.0):

                    s1 = shower_v.at(i)
                    s2 = shower_v.at(j)

                    radlen1 = RadLen( s1, xyz )
                    radlen2 = RadLen( s2, xyz )
                    radlen.append( radlen1 )
                    radlen.append( radlen2 )
                                   

                    e1 = s1.Energy()
                    e2 = s2.Energy()

                    angle = s1.Direction().Angle( s2.Direction() )
                    mass  = np.sqrt( 2 * e1 * e2 * (1 - np.cos(angle) ) )
                    masses.append(mass)
                    print 'E1 : %.02f \t E2 : %.02f \t angle = %.02f'%(e1,e2,angle*180/3.14)
                    print 'R1 : %.00f \t R1 : %.00f'%(radlen1,radlen2)
                    print
                    print 'MASS IS %.02f'%mass
                    print

#sys.exit(0)
print len(masses)

fig = plt.figure(figsize=(10,10))
plt.hist(masses,bins=np.linspace(0,500,20))
plt.grid()
plt.show()

fig = plt.figure(figsize=(10,10))
plt.hist(radlen,bins=np.linspace(0,70,15))
plt.grid()
plt.show()

fig = plt.figure(figsize=(10,10))
plt.hist(impact,bins=np.linspace(0,15,15))
plt.grid()
plt.show()
