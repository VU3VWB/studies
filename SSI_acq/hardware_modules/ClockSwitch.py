from casperfpga.clockswitch import HMC922

class ClockSwitch(HMC922):
    def __init__(self,fpga):
        self.fpga = fpga
        super(ClockSwitch, self).__init__(self.fpga,'adc16_use_synth')

    def set(self,source='synth'):
        if source == 'synth':
            self.setSwitch('a')
        elif source == 'external':
            self.setSwitch('b')