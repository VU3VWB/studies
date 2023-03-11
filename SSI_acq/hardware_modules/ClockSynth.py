from casperfpga.synth import LMX2581

class ClockSynth(LMX2581):
    def __init__(self,fpga):
        self.fpga = fpga
        super(ClockSynth, self).__init__(self.fpga,'lmx_ctrl', fosc=10)

    def set_frequency(self,freq=250):
        self.init()
        self.setFreq(freq)
        if not self.getDiagnoses('LD_PINSTATE'):
            raise Exception('Could not configure freq synth.')