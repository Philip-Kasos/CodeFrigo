import numpy as np 
import pyvisa


class PapaBox():
    def __init__(self, ip_address, read_termination):
        self.address = ip_address
        self.termin = read_termination
        self.handshake()
        print('Papa is home')

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        return

    def get_id(self):
        return self.client.query("*IDN?")

    def handshake(self):
        print("Handshake with BlueBox")
        self.rm = pyvisa.ResourceManager()
        self.client = self.rm.open_resource(self.address, timeout = 5000, read_termination = self.termin)
    

class BlueBox(PapaBox):
    def __init__(self, ip, termination = '\n'):
        super().__init__(ip_address = ip, read_termination = termination)
        print('Son is home')
        self.identity = self.get_id()
        print(self.identity)
    
    
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        return

        
    def set_freq(self, freq, channel):
        """
        Set the internal modulation frequency of the signal generator
        
        input:
        freq: float, frequency in MHz
        channel: int, channel number

        output:
        true_freq: float, the actual frequency set by the signal generator

        """

        header = f'source{channel}:am:internal:frequency'
        units = 'MHz'
        
        self.client.write(f"{header} {freq}{units}")

        true_freq = self.client.query(f"{header}?")
        print(f"Frequency set to {true_freq}")


    def set_function(self, func = 'triangle'):
        """
        Set the function of the signal generator
        
        input:
        func: str, function name

        output:
        true_func: str, the actual function set by the signal generator

        """

        header = f'am:internal:function'
        
        self.client.write(f"{header} {func}")

        true_func = self.client.query(f"{header}?")
        print(f"Function set to {true_func}")


    def set_amplitude(self, amp, channel):
        """
        Set the amplitude of the signal generator

        input:
        amp: float, amplitude of the signal peak-to-peak in V
        channel: int, channel number

        output:
        true_amp: float, the actual amplitude set by the signal generator

        """

        header = f'source{channel}:voltage'

        units = 'vpp'
        self.client.write(f"source{channel}:voltage:low 0V")
        self.client.write(f"{header} {amp}{units}")

        true_amp = self.client.query(f"{header}?")
        print(f"Amplitude set to {true_amp}")
        


    


if __name__ == "__main__":
    with BlueBox("USB0::0x0699::0x0343::C020325::INSTR", '\n') as bb:
        print("Use BlueBox as bb")
        import code; code.interact(local=locals())