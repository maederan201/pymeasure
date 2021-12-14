"""
This example demonstrates how to make a graphical interface with custom inputs,
and uses a random number generator to simulate data so that it does not require
an instrument to use. The gui_custom_inputs.ui file is loaded, which allows for
the custom inputs interface.

Run the program by changing to the directory containing this file and calling:

python gui_custom_inputs.py

"""

import sys
import random
import tempfile
from time import sleep

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

from pymeasure.log import console_log
from pymeasure.experiment import Procedure, IntegerParameter, Parameter, FloatParameter
from pymeasure.experiment import Results, Worker
from pymeasure.display.Qt import QtGui, fromUi
from pymeasure.display import Plotter
from pymeasure.display.windows import ManagedWindow, PlotterWindow


class TestProcedure(Procedure):

    iterations = IntegerParameter('Loop Iterations', default=10)
    delay = FloatParameter('Delay Time', units='s', default=0.01)
    seed = Parameter('Random Seed', default='12345')

    DATA_COLUMNS = ['Iteration', 'Random Number','e1','e2']

    def startup(self):
        log.info("Setting up random number generator")
        random.seed(self.seed)

    def execute(self):
        log.info("Starting to generate numbers")
        for i in range(self.iterations):
            data = {
                'Iteration': i,
                'Random Number': random.random(),
                'e1': random.random(),
                'e2': random.random()
            }
            log.debug("Produced numbers: %s" % data)
            self.emit('results', data)
            self.emit('progress', 100*i/self.iterations)
            sleep(self.delay)
            if self.should_stop():
                log.warning("Catch stop command in procedure")
                break

    def shutdown(self):
        log.info("Finished")


# class MainWindow(ManagedWindow):

#     def __init__(self):
#         super(MainWindow, self).__init__(
#             procedure_class=TestProcedure,
#             displays=['iterations', 'delay', 'seed'],s
#             x_axis='Iteration',
#             y_axis='Random Number'
#         )
#         self.setWindowTitle('GUI Example')

#     def _setup_ui(self):
#         super(MainWindow, self)._setup_ui()
#         self.inputs.hide()
#         self.inputs = fromUi('gui_custom_inputs.ui')

#     def queue(self):
#         filename = tempfile.mktemp()

#         procedure = TestProcedure()
#         procedure.seed = str(self.inputs.seed.text())
#         procedure.iterations = self.inputs.iterations.value()
#         procedure.delay = self.inputs.delay.value()

#         results = Results(procedure, filename)

#         experiment = self.new_experiment(results)

#         self.manager.queue(experiment)


if __name__ == "__main__":
    scribe = console_log(log, level=logging.DEBUG)
    scribe.start()

    filename = tempfile.mktemp()
    log.info("Using data file: %s" % filename)

    procedure = TestProcedure()
    procedure.iterations = 10
    procedure.delay = 0.01
    log.info("Set up TestProcedure with %d iterations" % procedure.iterations)

    results = Results(procedure, filename)
    log.info("Set up Results")

    plotter = Plotter(results,xerr='e1',yerr='e2')
    plotter.start()

    worker = Worker(results, scribe.queue, log_level=logging.DEBUG)
    log.info("Created worker for TestProcedure")
    log.info("Starting worker...")
    worker.start()

    log.info("Joining with the worker in at most 20 min")
    worker.join(60*20)
    log.info("Waiting for Plotter to close")
    plotter.wait_for_close()
    log.info("Plotter closed")

    log.info("Stopping the logging")
    scribe.stop()



