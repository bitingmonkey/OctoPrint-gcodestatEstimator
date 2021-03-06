# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import logging

import re

from octoprint.printer.estimation import PrintTimeEstimator


class M73ProgressTimeVisualizer(PrintTimeEstimator):
    def __init__(self, job_type,printer, file_manager, logger, current_history):
        super(M73ProgressTimeVisualizer, self).__init__(job_type)
        self._job_type = job_type
        self.estimated_time = 0
        self.percentage_done = -1
        self._logger = logger

    def estimate(self, *args, **kwargs):
        # if self._job_type != "local" or self.percentage_done == -1:
        #     return PrintTimeEstimator.estimate(self, *args, **kwargs)
        self._logger.debug("M73Progress estimate: {}sec".format(self._estimator.estimated_time))
        return 6 * 60 * 60, "estimate"

class M73ProgressTimeVisualizerPlugin(octoprint.plugin.StartupPlugin):

    pw = re.compile('M73 P([0-9]+) R([0-9]+)')

    def __init__(self):
        self._estimator = None

    def on_after_startup(self):
        self._logger.info("Started up M73Progress")


    ##~~ queuing gcode hook

    def updateEstimation(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
        if gcode != "M73" or self._estimator is None:
            return

        mw = self.pw.match(cmd)
        if mw:
            self._estimator.estimated_time = float(mw.group(2))*60 
            self._estimator.percentage_done = float(mw.group(1))
        else :
            return

        self._logger.debug("M73Progress: {}% {}sec".format(self._estimator.percentage_done, self._estimator.estimated_time))

    ##~~ estimator factory hook

    def estimator_factory(self):
        def factory(*args, **kwargs):
            self._estimator = M73ProgressTimeVisualizer(*args, **kwargs)
            return self._estimator
        return factory

    ##~~ software update hook

    def get_update_information(self):
        return dict(
            gcodestatEstimator=dict(
                displayName=self._plugin_name,
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="bitingmonkey",
                repo="OctoPrint-M73Progress",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/bitingmonkey/OctoPrint-M73TimeVisualizer/archive/{target_version}.zip"
            )
        )


__plugin_implementation__ = M73ProgressTimeVisualizerPlugin()
__plugin_hooks__ = {
    "octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.updateEstimation,
    "octoprint.printer.estimation.factory": __plugin_implementation__.estimator_factory,
    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}
