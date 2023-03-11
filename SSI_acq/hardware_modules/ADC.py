from casperfpga.snapadc import SNAPADC
import numpy as np

class ADC(SNAPADC):

    def __init__(self,fpga,n_inputs,sampling_rate):
        super(ADC, self).__init__(fpga)
        self.fpga = fpga
        self.resolution = 8
        self.n_inputs = n_inputs
        self.sampling_rate = sampling_rate
        #self.gains = [11]*self.n_inputs # --- 11 corresponds to x25 voltage gain & 200mV range pk/pk
        self.gains = [6]*self.n_inputs # --- 0 corresponds to x1 voltage gain & 5000mV range pk/pk
        #self.gains = [12]*self.n_inputs # --- 12 corresponds to x32 voltage gain & 156.25mV range pk/pk



    def configure(self):
        """
        Configures and Calibrates the ADC chips on startup. 
        """
        # ---- determine if lowClkFreq mode is requred -----
        if self.n_inputs==3 and self.sampling_rate<240:
            lowClkFreq = True
        elif self.n_inputs==6 and self.sampling_rate<120:
            lowClkFreq = True
        elif self.n_inputs==12 and self.sampling_rate<60:
            lowClkFreq = True
        else:
            lowClkFreq = False

        # ---- Initialise ADC's ----
        self.reset()
        self.selectADC()
        self.adc.init(numChannel=self.n_inputs/3, clkDivide=1,lowClkFreq=lowClkFreq)

        # ---- Calibrate ADC Clocks ----
        self.setDemux(1) 
        if not self.getWord('ADC16_LOCKED'):
            return self.ERROR_MMCM

        attempts = 5

        for i in range(attempts):
            if self.alignLineClock():
                break
            else:
                if i == attempts -1:
                    raise IOError('Failed to align line clock after ' + str(attempts) + ' attempts.' )

        for i in range(attempts):
            if self.alignFrameClock():
                break
            else:
                if i == attempts -1:
                    raise IOError('Failed to align frame clock after ' + str(attempts) + ' attempts.' )

        errs = self.testPatterns(mode='ramp')
        if not np.all(np.array([adc.values() for adc in errs.values()])==0):
            raise IOError('ADCs failed RAMP tests')
            return self.ERROR_RAMP

        # ---- Configure Operating Mode ----
        self.selectADC() # send commands to all ADC chips
        if self.n_inputs == 12:
            self.adc.selectInput([1,2,3,4]) # Four Channel Mode
        elif self.n_inputs == 6:
            self.adc.selectInput([1,1,3,3]) # Two Channel Mode
        else:
            self.adc.selectInput([1,1,1,1]) # One Channel Mode
        self.setDemux(self.n_inputs/3)

        # ---- Init Course_Gains ----
        if self.n_inputs == 12:
            g = [self.gains[0:4],self.gains[4:8],self.gains[8:12]]
        elif self.n_inputs == 6:
            g = [self.gains[0:2],self.gains[2:4],self.gains[4:6]]
        elif self.n_inputs == 3:
            g = self.gains

        self.selectADC()
        self.adc.write( 0x0003  , 0x33 ) # Enable fGain & set cGain to linear mode
        for chip in range(3):
            self.selectADC(chip)
            # Write cGains into corresponding register depending on mode
            if self.n_inputs == 12:
                data = (g[chip][3]<<12) | (g[chip][2]<<8) | (g[chip][1]<<4) | g[chip][0]
                self.adc.write( data  , 0x2A )
            elif self.n_inputs == 6:
                data = ( g[chip][1]<<4 | g[chip][0] )
                self.adc.write( data  , 0x2B )
            elif self.n_inputs == 3:
                data = (g[chip]<<8)
                self.adc.write( data  , 0x2B )

        self.selectADC()
        return self.SUCCESS


    def get_snapshot(self,input):
        """
        Returns a 1024 sample snapshot of the ADC chips. Some formatting may be required depending on the Demux mode.
        """
        self.snapshot()

        if self.n_inputs == 3:
            chip = input
            chip_in = 0
        elif self.n_inputs == 6:
            chip = int(input/2)
            chip_in = int(input%2)
        elif self.n_inputs == 12:
            chip = int(input/4)
            chip_in = int(input%4)

        snapshot = np.reshape( self.readRAM( ram=chip ) , [256,4] )

        demux = int(12 / self.n_inputs)
        temp = []
        for n in range( demux ):
            temp.append( snapshot[:,demux*chip_in + n] )
        data = np.reshape( temp , [256*demux] )

        return ( data / float(2**7) )

