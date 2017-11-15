import sys

if len(sys.argv) < 2:
    msg  = '\n'
    msg += "Usage 1: %s $INPUT_ROOT_FILE\n" % sys.argv[0]
    msg += '\n'
    sys.stderr.write(msg)
    sys.exit(1)


# Import the needed modules.  Need larlite and several of it's namespaces
from ROOT import gSystem,TMath
from larlite import larlite as fmwk
from larlite import larutil
from recotool import cmtool, showerreco
from ROOT import protoshower
from ROOT import calo
# from recotool.showerDef import DefaultShowerReco3D



def getShowerRecoAlgModular():
    # This function returns the default shower reco module
    # If you want to extend, customize, or otherwise alter the default
    # reco (which you should!) it's recommended that you do one of two
    # things:
    #   1) Copy this function, and change the lines you need
    #   2) Use this function as is and replace the modules with the built-in functions
    #       to ShowerRecoAlgModular
    # Then, use the return value (alg) in place of ShowerRecoAlg in your python script
    
    # It should be noted, however, that this "default" set of modules is not yet developed
    # and if you are developing you ought to be updating it here!
    
    alg = showerreco.ShowerRecoAlgModular()
    alg.SetDebug(True)
    alg.SetVerbose(False)

    filteralgo = showerreco.FilterPFPart()
    filteralgo.setMinNHitsAbsolute(5)
    filteralgo.setMinNHitsLargest(10)
    
    angle3D = showerreco.Angle3DFormula()
    angle3D.setMaxAngleError(0.1)
    angle3D.setValidateDirection(True)
    angle3D.setVerbosity(False)

    angle3D = showerreco.Angle3DFromVtxQweighted()

    startPt = showerreco.YPlaneStartPoint3D()
    startPt.setVerbosity(False)

    energy = showerreco.LinearEnergy()
    energy.SetElectronLifetime(1e6  ) # in us DATA value
    energy.SetRecombFactor(0.62)
    energy.SetElecGain(243.) # MCC8.0 data
    #energy.SetElecGain(200.) # MCC8.0 value
    energy.setVerbosity(False)
    energy.SetFillTree(True)

    dqdx = showerreco.dQdxModule()
    
    dedx = showerreco.dEdxFromdQdx()
    dedx.SetUsePitch(False)
    dedx.setVerbosity(True)

    shrFilter = showerreco.FilterShowers()
    shrFilter.setAngleCut(15.)
    shrFilter.setVerbosity(True)

    alg.AddShowerRecoModule( filteralgo )
    alg.AddShowerRecoModule(angle3D)
    #alg.AddShowerRecoModule( showerreco.StartPoint3DModule() )
    #alg.AddShowerRecoModule( showerreco.NearestStartPoint3D() )
    alg.AddShowerRecoModule( startPt )#showerreco.YPlaneStartPoint3D() )
    alg.AddShowerRecoModule(energy)
    alg.AddShowerRecoModule( showerreco.FillLength() )
    alg.AddShowerRecoModule( shrFilter )
    
    alg.PrintModuleList()
    
    return alg

def DefaultShowerReco3D():
    
    # Create analysis unit
    ana_unit = fmwk.ShowerReco3D()
    
    # require PDG == 11 for PFParticles
    ana_unit.SetRequirePDG11(False)
    
    # Attach shower reco alg
    sralg = getShowerRecoAlgModular()
    # sralg.SetDebug()
    # sralg.Verbose(False)
    # sralg.Verbose(True)
    # sralg.SetUseArea(True)
    # Attach calo alg
    # calg = calo.CalorimetryAlg()
    # sralg.CaloAlgo(calg)
    #sralg.SetUseModBox(True)
    ana_unit.AddShowerAlgo(sralg)

    return ana_unit


# Create ana_processor instance
my_proc = fmwk.ana_processor()

# Set input root file
for x in xrange(len(sys.argv)-1):
    my_proc.add_input_file(sys.argv[x+1])

# Specify IO mode
my_proc.set_io_mode(fmwk.storage_manager.kBOTH)

# Specify analysis output root file name
my_proc.set_ana_output_file("showerRecoUboone_ana.root")
# Specify data output root file name
my_proc.set_output_file("showerRecoUboone_data_debug.root")


ana_unit=DefaultShowerReco3D()
# set ProtoShower Algo to go from data-products to a ProtoShower object
protoshoweralg = protoshower.ProtoShowerAlgCMTool()
#protoshoweralg = protoshower.ProtoShowerAlgOpenCV()
ana_unit.GetProtoShowerHelper().setProtoShowerAlg( protoshoweralg )

#ana_unit.SetInputProducer("ImageClusterHit")
ana_unit.SetInputProducer("iou")

ana_unit.SetOutputProducer("showerreco")

my_proc.add_process(ana_unit)

#my_proc.set_data_to_write(fmwk.data.kMCTruth,     "generator")
#my_proc.set_data_to_write(fmwk.data.kMCShower,    "mcreco")
#my_proc.set_data_to_write(fmwk.data.kMCShower,     "mcreco")
#my_proc.set_data_to_write(fmwk.data.kVertex,       "sel2")
#my_proc.set_data_to_write(fmwk.data.kShower,       "showerreco")
#my_proc.set_data_to_write(fmwk.data.kAssociation,  "showerreco")

print
print  "Finished configuring ana_processor. Start event loop!"
print

my_proc.run(324,1)
# my_proc.process_event(2)



sys.exit()

