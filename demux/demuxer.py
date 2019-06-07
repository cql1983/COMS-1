"""
demuxer.py
https://github.com/sam210723/COMS-1
"""

from collections import deque
from time import sleep
from threading import Thread

from VCDU import VCDU

class Demuxer:
    """
    Coordinates demultiplexing of CCSDS virtual channels into xRIT files.
    """

    def __init__(self, downlink):
        """
        Initialises demuxer class
        """
        
        # Configure instance globals
        self.rxq = deque()             # Data receive queue
        self.coreReady = False         # Core thread ready state
        self.coreStop = False          # Core thread stop flag
        
        if downlink == "LRIT":
            self.coreWait = 54         # Core loop delay in ms for LRIT (108.8ms per packet @ 64 kbps)
        elif downlink == "HRIT":
            self.coreWait = 1          # Core loop delay in ms for HRIT (2.2ms per packet @ 3 Mbps)

        # Start core demuxer thread
        demux_thread = Thread()
        demux_thread.name = "DEMUX CORE"
        demux_thread.run = self.demux_core
        demux_thread.start()


    def demux_core(self):
        """
        Demuxer core thread entry point
        """
        
        # Indicate core thread has initialised
        self.coreReady = True

        while not self.coreStop:
            # Pull next packet from queue
            packet = self.pull()

            if packet != None:
                # Packet available
                continue
            else:
                # No packet available, sleep thread
                sleep(self.coreWait / 1000)
        
        # Gracefully exit core thread
        if self.coreStop:
            return
    

    def push(self, packet):
        """
        Takes in VCDUs for the demuxer to process
        :param packet: 892 byte Virtual Channel Data Unit (VCDU)
        """

        self.rxq.append(packet)

    def pull(self):
        """
        Pull data from receive queue
        """

        try:
            # Return top item
            return self.rxq.popleft()
        except IndexError:
            # Queue empty
            return None

    def complete(self):
        """
        Checks if receive queue is empty
        """

        if len(self.rxq) == 0:
            return True
        else:
            return False

    def stop(self):
        """
        Stops the demuxer loop by setting thread stop flag
        """

        self.coreStop = True
