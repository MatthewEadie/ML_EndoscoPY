"""Example of CO pulse time operation."""
import time

import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.types import CtrTime


with nidaqmx.Task() as task:
    task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr0",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 0 
    task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr1",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 3
    # task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr2",initial_delay=0.0, low_time=0.5, high_time=0.5) #I/O channel 1 
    # task.co_channels.add_co_pulse_chan_time("cDAQ_VER/ctr3",initial_delay=0.1, low_time=0.15, high_time=0.05) I/O channel 2
    # task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.CONTINUOUS)
    task.timing.cfg_implicit_timing(sample_mode=AcquisitionType.FINITE, samps_per_chan=10)
    task.start()

    while(not(task.is_task_done())):
            task.is_task_done()

