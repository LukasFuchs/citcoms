#!/usr/bin/env python
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# <LicenseText>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

from mpi.Application import Application
import journal


class TestExchanger(Application):

    def __init__(self, name="citcom"):
        Application.__init__(self, name)
        self.exchanger = None
        return



    def run(self):
        layout = self.inventory.layout
        layout.initialize(self)

        self.findLayout(layout)

        # a dummy pointer for test only
        import CitcomS.Exchanger
        self.all_variables = CitcomS.Exchanger.returnE()

        exchanger = self.exchanger
        if exchanger:
            self.test(exchanger)

        return


    def test(self, exchanger):
        # testing exchanger creation
        exchanger.selectModule()
	exchanger.createExchanger(self)
        print exchanger.name, exchanger.exchanger

        # testing boundary creation and exchange
        boundary = exchanger.findBoundary()
        print exchanger.name, boundary

        try:
            # success if exchanger is a FGE
            exchanger.catchup
            dt = 0.15
        except:
            # exception if exchanger is a CGE
            dt = 1

        # testing dt exchanging
        print "%s - old = %f   exchanged = %f   old = %f" % (exchanger.name,
              dt, exchanger.module.exchangeTimestep(exchanger.exchanger, dt),
              dt)

        # testing wait & nowait
        for step in range(7*2+1):
            exchanger.NewStep()
            time = exchanger.stableTimestep(dt)
            print "%s - step %d: %f" % (exchanger.name, step, time)

        return



    def findLayout(self, layout):
        if layout.coarse:
            self.exchanger = self.inventory.coarse
            self.communicator = layout.coarse
        elif layout.fine:
            self.exchanger = self.inventory.fine
            self.communicator = layout.fine
        else:
            import journal
            journal.warning(self.name).log("node '%d' is an orphan" % layout.rank)
        self.intercomm = layout.intercomm
        self.rank = layout.rank
        self.nodes = layout.nodes
        self.localLeader = layout.localLeader
        self.remoteLeader = layout.remoteLeader

        print self.exchanger.name, self.rank, \
              self.localLeader, self.remoteLeader

        return




    class Inventory(Application.Inventory):

        import pyre.facilities

        import CitcomS.Components.Exchanger as Exchanger
        import CitcomS.Controller as Controller
        import CitcomS.Layout as Layout

        inventory = [

            pyre.facilities.facility("controller", default=Controller.controller()),
            pyre.facilities.facility("layout", default=Layout.layout()),

            pyre.facilities.facility("coarse", default=Exchanger.coarsegridexchanger("coarse", "coarse")),
            pyre.facilities.facility("fine", default=Exchanger.finegridexchanger("fine", "fine")),

            ]



# main

if __name__ == "__main__":

    import mpi

    # testing Exchangermodule.so
    import CitcomS.Exchanger
    if not mpi.world().rank:
        print CitcomS.Exchanger.copyright()
        print dir(CitcomS.Exchanger)


    app = TestExchanger("test")
    app.main()



# version
__id__ = "$Id: exchange.py,v 1.4 2003/09/10 04:00:31 tan2 Exp $"

# End of file