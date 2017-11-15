import ROOT
import os,sys
from ROOT import larutil

class DeadWires():

    def __init__(self):

        self._badchannels = [[],[],[]]
        self.getBadWireMap()

    def getBadWireMap(self):

        # reset bad channel list
        self._badchannels = [[],[],[]]

        Geo = larutil.Geometry.GetME()

        if (os.path.isfile('%s/DisplayTool/python/channel.html'%os.environ['LARLITE_USERDEVDIR']) == False):
        
            cmd = 'wget \'http://dbdata0vm.fnal.gov:8186/uboonecon_prod/app/data?f=channelstatus_data&t=1450000000\' -O %s/DisplayTool/python/channel.html'%os.environ['LARLITE_USERDEVDIR']
            os.system(cmd)

        fin = open('%s/DisplayTool/python/channel.html'%os.environ['LARLITE_USERDEVDIR'])

        ctr = 0
        
        for line in fin:

            ctr += 1
            
            text  = line.split()[0]
            words = text.split(",")

            if (len(words) != 2): continue

            if (ctr < 5): continue
            
            chan   = int(words[0])
            status = int(words[1])
                                
            if (status < 3): # status is bad
                
                wID = Geo.ChannelToWireID(chan)
                plane  = wID.Plane
                wire   = wID.Wire
                self._badchannels[plane].append( wire )
                

    def getBadCoverage(self, x, y, z, ROI):

        coverage = [0.,0.,0.]

        xyz = ROOT.TVector3(x,y,z)

        geo  = larutil.Geometry.GetME()
        geoH = larutil.GeometryHelper.GetME()

        w2cm = geoH.WireToCm()

        #print 'vtx @ [%i,%i,%i]'%(x,y,z)

        for pl in xrange(3):

            wire = geo.NearestWire(xyz,pl)

            #print ' @ plane %i nearest wire is %i'%(pl,wire)

            wmin = wire - int(ROI / w2cm)
            wmax = wire + int(ROI / w2cm)

            badchan_v = self._badchannels[pl]

            badchan = 0.
            
            for chan in badchan_v:
                
                if (chan < wmin): continue

                badchan += 1

                if (chan > wmax): break;

            #print 'bad channel coverage = %.02f'%(badchan/(wmax-wmin))

            coverage[pl] = float(badchan)/(wmax-wmin)

        return coverage
                
            
            
