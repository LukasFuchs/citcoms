#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# <LicenseText>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

from Exchanger import Exchanger

class FineGridExchanger(Exchanger):


    def __init__(self, name, facility):
        Exchanger.__init__(self, name, facility)
        self.catchup = True
        self.cge_t = 0
        self.fge_t = 0
        return



    def createExchanger(self, solver):
        self.exchanger = self.module.createFineGridExchanger(
                                     solver.communicator.handle(),
                                     solver.intercomm.handle(),
                                     solver.localLeader,
                                     solver.remoteLeader,
                                     solver.all_variables
                                     )
        return



    def findBoundary(self):
        boundary = self.module.createBoundary(self.exchanger)

        # send boundary from CGE
        self.module.sendBoundary(self.exchanger, boundary)

	# create mapping from boundary to id array
	self.module.mapBoundary(self.exchanger, boundary)
        return boundary



    def initTemperature(self):
        # receive temperture field from CGE
        self.module.receiveTemperature(self.exchanger)
        return



    def NewStep(self):
        if self.catchup:
            # send wakeup signal to CGE
            self.module.nowait(self.exchanger)

            # send temperture field to CGE
            #self.module.sendTemperature(self.exchanger)

        return



    def applyBoundaryConditions(self):
        self.module.gather(self.exchanger)
        self.module.send(self.exchanger)
        return



    def stableTimestep(self, dt):
        if self.catchup:
            self.cge_t = self.module.exchangeTimestep(self.exchanger, dt)
            self.fge_t = 0
            self.catchup = False

        self.fge_t += dt

        if self.fge_t >= self.cge_t:
            dt = dt - (self.fge_t - self.cge_t)
            self.catchup = True

        return dt



    class Inventory(Exchanger.Inventory):

        import pyre.properties as prop


        inventory = [

            ]



# version
__id__ = "$Id: FineGridExchanger.py,v 1.4 2003/09/10 04:01:53 tan2 Exp $"

# End of file