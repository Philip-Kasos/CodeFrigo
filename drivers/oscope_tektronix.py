import numpy as np
import pyvisa
import os
import sys
import matplotlib.pyplot as plt

abs_path = os.path.abspath(os.path.dirname(__file__))
if abs_path not in sys.path:
    sys.path.append(abs_path)

print(sys.path)

class tekscope:
    def __init__(self, ip, termination):
        self.address = ip
        self.termin = termination
        self.handshake()
        print('Tektronix scope is home')
        self.identity = self.get_id()
        print(self.identity)

        self.get_data_depth()
        print(self.data_byte_depth)
        print(self.get_vert(2), "mV/div")
        print(self.get_vert_offset(2))

        self.set_data_start(1)
        self.set_data_stop(100000)
        self.save_trace(2)
    
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        return
    
    def get_id(self):
        return self.client.query("*IDN?")
    
    def handshake(self):
        print("Handshake with Tektronix scope")
        self.rm = pyvisa.ResourceManager()
        self.client = self.rm.open_resource(self.address, timeout = 5000,
                                            read_termination = self.termin,
                                            )

    def set_time(self, scale):
        """
        Set the horizontal time scale of the oscilloscope.
        
        Parameters:
        scale (float): The time scale in seconds/div. Range: 5ns to 50s. Given in ms.

        """
        head = f"horizontal:scale"

        self.client.write(f"{head} {scale}E-3")

    def get_time(self):
        """
        Get the horizontal time scale of the oscilloscope.
        
        Returns:
        time (float): The actual time scale set by the oscilloscope.
        
        """

        head = f"horizontal:scale"
        time = self.client.query(f"{head}?")
        return time
    
    def set_vert(self, channel, scale):
        """
        Set the vertical scale of the oscilloscope for a given channel.
        
        Parameters:
        channel (int): The channel number (1, 2, 3 or 4).
        scale (float): The vertical scale in Volts/div. Range: 2mV to 10V.

        """
        
        head = f"ch{channel}:scale"
        self.client.write(f"{head} {scale}E+0")

    def get_vert(self, channel):
        """
        Get the vertical scale of the oscilloscope for a given channel.
        
        Parameters:
        channel (int): The channel number (1, 2, 3 or 4).
        
        Returns:
        vert (float): The actual vertical scale set by the oscilloscope.
        
        """

        head = f"ch{channel}:scale"
        vert = self.client.query(f"{head}?")
        return vert
    
    def set_vert_offset(self, channel, offset):
        """
        Set the vertical offset of the oscilloscope for a given channel.
        
        Parameters:
        channel (int): The channel number (1, 2, 3 or 4).
        offset (float): The vertical offset in Volts. Range: -8 to 8V.

        """
        
        head = f"ch{channel}:offset"
        self.client.write(f"{head} {offset}E+0")

    def get_vert_offset(self, channel):
        """
        Get the vertical offset of the oscilloscope for a given channel.
        
        Parameters:
        channel (int): The channel number (1, 2, 3 or 4).
        
        Returns:
        offset (float): The actual vertical offset set by the oscilloscope.
        
        """

        head = f"ch{channel}:offset"
        offset = self.client.query(f"{head}?")
        return offset
    
    def get_ch_source(self):
        """
        Get the source of the channel.
        
        Parameters:
        channel (int): The channel number (1, 2, 3 or 4).
        
        Returns:
        source (str): The source of the channel.
        
        """
        source = self.client.query(f"data:source?")
        return source
    
    def set_ch_source(self, channel: int):
        """
        Set the source of the channel.
        
        Parameters:
        channel (int): The channel number (1, 2, 3 or 4).
        
        """
        self.client.write(f"data:source ch{channel}")

    def get_data_start(self):
        """
        Get the start of the data.
        
        Returns:
        start (int): The start of the data.
        
        """
        start = self.client.query(f"data:start?")
        return start

    def set_data_start(self, start):
        """
        Set the start of the data.
        
        Parameters:
        start (int): The start of the data.
        
        """
        self.client.write(f"data:start {start}")
        return 
    
    def get_data_stop(self):
        """
        Get the stop of the data.
        
        Returns:
        stop (int): The stop of the data.
        
        """
        stop = self.client.query(f"data:stop?")
        return stop
    
    def set_data_stop(self, stop):
        """
        Set the stop of the data.
        
        Parameters:
        stop (int): The stop of the data.
        
        """
        self.client.write(f"data:stop {stop}")
        return


    def ready(self):
        """
        Check if the oscilloscope is ready.
        
        Returns:
        status (str): The status of the oscilloscope.
        
        """
        status = self.client.query("*OPC?")
        return status

    def get_trace(self, channel):
        """
        Get the trace of the oscilloscope for a given channel.
        
        Parameters:
        state (str): The state of the oscilloscope (OFF, ON, RUN, STOP | int -> 0 = stop, else start).
        
        Returns:
        trace (numpy array): The trace of the oscilloscope for the given channel.
        
        """
        self.set_ch_source(channel)
        vert_scale = self.get_vert(channel)
        vert_offset = self.get_vert_offset(channel)
        ans = None
        self.ready()
        self.client.write(f"curve?")
        raw_data = self.client._read_raw()
        if raw_data[:1] == b'#':
            num_digits = int(raw_data[1:2])
            num_bytes = int(raw_data[2:2+num_digits])
            data = raw_data[2+num_digits: 2+num_digits+num_bytes]
            data = np.frombuffer(data, dtype = self.data_type) - self.mid_level
            data = data
            ans = data

        plt.plot(ans)
        plt.show()
        print(ans)
        return ans
    
    def get_data_format(self):
        """
        Get the data format of the oscilloscope.
        
        Returns:
        format (str): The data format of the oscilloscope.
        
        """
        ans = self.client.query(f"WFMOutpre:PT_Fmt?")
        return ans

    def get_data_depth(self):
        """
        Get the data depth of the oscilloscope.
        
        Returns:
        depth (int): The data depth of the oscilloscope.
        
        """
        ans = self.client.query(f"WFMOutpre:BYT_Nr?")
        self.data_byte_depth = int(ans)
        if self.data_byte_depth == 1:
            self.data_type = np.uint8
            self.mid_level = 128
        elif self.data_byte_depth == 2:
            print('hihi')
            self.data_type = np.uint16
            self.mid_level = 32768
        return ans

    def save_trace(self, channel):
        """
        Save the trace of the oscilloscope for a given channel.
        
        Parameters:
        channel (int): The channel number (1, 2, 3 or 4).
        
        """
        trace = self.get_trace(channel)
        np.save(abs_path + f"/../output/trace_ch{channel}.npy", trace)


        return

if __name__ == "__main__":
    with tekscope("USB0::0x0699::0x0374::C011064::INSTR", '\n') as ts:
        print("Use tekscope as ts")
        import code; code.interact(local=locals())   
        
        