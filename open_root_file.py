import numpy as np 
import uproot
import time

run_data = np.array([])

def store_data(filepath):

    global run_data

    DY_tree = uproot.open(filepath)["save;1"]

    

    detID = DY_tree["rawEvent/fAllHits/fAllHits.detectorID"].array(library="np")

    elemID = DY_tree["rawEvent/fAllHits/fAllHits.elementID"].array(library="np")

    drift = DY_tree["rawEvent/fAllHits/fAllHits.driftDistance"].array(library="np")

    #gpx = DY_tree["gpx"].arrays(library="np")["gpx"]
    #gpy = DY_tree["gpy"].arrays(library="np")["gpy"]
    #gpz = DY_tree["gpz"].arrays(library="np")["gpz"]

    #gvx = DY_tree["gvx"].arrays(library="np")["gvx"]
    #gvy = DY_tree["gvy"].arrays(library="np")["gvy"]
    #gvz = DY_tree["gvz"].arrays(library="np")["gvz"]

    #run_data = np.array([gpx, gpy, gpz, gvx, gvy, gvz])
    run_data = np.array([detID, elemID, drift])

#DY_tree = uproot.open('Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root')["save;1"]
#print("Branches:", DY_tree.keys())

store_data('Jay/run_data/run_005591/run_005591_spill_001903474_sraw.root')
#print(run_data[0])
print(uproot.open('/home/uvaspin/Jay/run_data/run_005593/run_005593_spill_001903711_sraw.root').closed)





