import numpy as np
import pyvisa
import os


class Kidbox():
    def __init__(self, ip_address, read_termination):
        self.address = ip_address
        self.termin = read_termination
        self.handshake()
        print('Kid is home')

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return

    def get_id(self):
        return self.client.query("*IDN?")

    def handshake(self):
        print("Handshake with Kidbox")
        self.rm = pyvisa.ResourceManager()
        self.client = self.rm.open_resource(self.address, timeout = 5000, read_termination = self.termin)
    
    def run(self):
        self.client.write(":RUN")

    def stop(self):
        self.client.write(":STOP")


    def vert_scale(self, channel, scale):
        """
        Set the vertical scale of the oscilloscope for a given channel.

        Parameters:
        channel (int): The channel number (1 or 2).
        scale (float): The vertical scale in Volts/div. Range: 2mV to 10V.

        Returns:
        true_scale (float): The actual scale set by the oscilloscope.
        """

        header = f":channel{channel}:scale"
        self.client.write(f"{header} {scale}E+0")

        true_scale = self.client.query(f"{header}?")
        return true_scale
    
    def set_time(self, scale):
        """
        Set the horizontal time scale of the oscilloscope.

        Parameters:
        scale (float): The time scale in seconds/div. Range: 5ns to 50s. Given in ms.

        Returns:
        true_scale (float): The actual time scale set by the oscilloscope.
        """

        header = ":timebase:scale"
        self.client.write(f"{header} {scale}E-3")

    def get_time(self):
        header = ":timebase:scale?"
        ans = self.client.query(f"{header}")
        return ans

    def get_channel_trace(self):
        
        header = f":acquire:RECOrdlength?"
        trace = self.client.query(header)

        return trace

    def get_interpolation(self):
        header = ":acquire:interpolation?"
        ans = self.client.query(header)
        return ans

    





if __name__ == "__main__":
    with Kidbox("ASRL3::INSTR", '\n') as kb:
        print("Use Kidbox as kb")
        import code; code.interact(local=locals())

        
        