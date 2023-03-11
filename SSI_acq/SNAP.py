from casperfpga import CasperFpga
from casperfpga.transport_tapcp import TapcpTransport
from hardware_modules import *
import struct
import time

class SNAP(object):

    def __init__(self,ip,firmware,clk_src='internal',adc_inputs=12,sampling_rate=250):
        """
        The SNAP class provides a simple mechanism to connect, configure and communicate with a SNAP board.
        :param ip: The IP address of the SNAP
        :param firmware: Filepath pointing to the firmware that is to be loaded onto the SNAP board.
        :param clk_src: The clock source. Valid inputs are ['internal','synth','external'].
        :param adc_inputs: Specifies which mode to operate the SNAP board. It must be either 3, 6 or 12.
        :param sampling_rate: The FPGA clock frequency in MHz
        """
        # ---- Validate Input ----
        if ip is None:
            raise ValueError('An IP address must be provided.')
        self.ip = ip

        if firmware is None:
            raise ValueError('The firmware filepath must be provided.')
        self.firmware = firmware

        if clk_src not in ['internal','synth','external']:
            raise ValueError('The clock source must be either "internal", "synth" or "external" ')
        self.clk_src = clk_src

        if adc_inputs not in [3,6,12]:
            raise ValueError('The number of ADC inputs can only be 3, 6 or 12.')
        self.adc_inputs = adc_inputs

        if sampling_rate*(12/self.adc_inputs) > 1000.0:
            raise ValueError('The sampling rate cannot be higher than (1000 MHz *adc_inputs/12).')
        self.sampling_rate = sampling_rate

        # ---- Connect to SNAP board ----
        self.fpga = None
        try:
            self.fpga = CasperFpga(self.ip, transport=TapcpTransport)
            #self.fpga.get_system_information(self.firmware)
        except:
            raise IOError('Failed to connect to SNAP')

        # --- Hardware Objects ---
        self.clock_synth = ClockSynth(self.fpga)
        self.clock_switch = ClockSwitch(self.fpga)
        self.adc = ADC(self.fpga,n_inputs=self.adc_inputs,sampling_rate=self.sampling_rate)


    def reload_firmware(self):
        """
        This will program the FPGA firmware before configuring the clock switch & clock synthesiser.
        """
        # ----- Program Firmware To SNAP -----
        self.fpga.upload_to_ram_and_program(self.firmware)

        # ---- Wait until SNAP is reachable ----
        done = False
        for i in range(60):
            time.sleep(1)
            if self.fpga.is_connected():
                done = True
                break
        if done == False:
            raise IOError('Failed to reconnect after 1 minute.')

        # ---- Configure Clock ----
        if self.clk_src != 'internal':
            self.clock_switch.set(self.clk_src)
            if self.clk_src == 'synth':
                self.clock_synth.set_frequency( self.sampling_rate )
            self.adc.configure()


    # ------------------- Communication Functions ------------------------
    def write_register(self,reg_name,data):
        """
        Write an integer to a register.
        :param reg_name: The name of the register.
        :param data: Data to write.
        :return:
        """
        self.fpga.write_int(reg_name, data )

    def read_register(self,reg_name,signed=True):
        """
        Read a register
        :param reg_name: Name of the register to read.
        :return:
        """
        if signed:
            return self.fpga.read_int(reg_name)
        else:
            return self.fpga.read_uint(reg_name)

    def write_bram(self,ram_name, data_in, data_width=4, addr=0):
        """
        Write to Block RAM a single row at a time.
        This function cannot support a data width greater than 32 bits yet (4 Bytes). 
        :param ram_name: memory device name to write
        :param data_in: data to write (int or float)
        :param data_width: data width in bytes
        :param addr: The row in which to write the data.
        :return:
        """
        if(data_width>8):
            raise ValueError("This method doesn't support data_width's greater than 8")
        data_in = int(data_in)

        data_in = data_in % (2**(8*data_width)) # convert signed negatives to undigned positives, be carefull this will wrap

        if data_width == 1:
            UF = 'B'
        elif data_width == 2:
            UF = 'H'
        elif data_width == 4:
            UF = 'I'
        elif data_width == 8:
            UF = 'Q'

        byte_addr = addr*data_width
        packed_data = struct.pack('>'+UF, data_in )
        self.write_block_bram(ram_name,packed_data,byte_addr)


    def read_bram(self,ram_name, data_width=4, sign='unsigned' , addr=0):
        """
        Read from Block RAM a single row at a time. 
        Unfortunately the casperfpga.read() function cannot read blocks smaller than 4 bytes at a time 
        and at address locations that are not a multiples of 4. This function allows us to do that!
        :param ram_name: memory device name to read
        :param data_width: data width in bytes
        :param signed: return 'signed' or 'unsigned' numbers
        :param addr: addr at which to read, the row number
        :return:
        """
        if data_width == 1:
            UF = 'B'
            F = 'b'
        elif data_width == 2:
            UF = 'H'
            F = 'h'
        elif data_width == 4:
            UF = 'I'
            F = 'i'
        elif data_width == 8:
            UF = 'Q'
            F = 'q'

        if sign == 'signed':
            signed = True
        else:
            signed = False

        byte_addr = addr*data_width
        packed = self.read_block_bram(ram_name,data_width,byte_addr)
        data = struct.unpack('>'+F if signed else '>'+UF, packed)[0]
        return data


    def write_block_bram(self,ram_name, data, byte_addr):
        """
        Write a large packed string of bytes to ram. No limitations of address or size, no need to be 32-bit bounded words.
        :param ram_name: Name of the BRAM to read
        :param data: The data to write
        :param byte_addr: The byte address to start reading the block
        """
        addr = (byte_addr//4)*4
        head_bytes = byte_addr % 4
        size = (head_bytes+len(data)-1)//4 + 1
        total_bytes = size*4
        tail_bytes = total_bytes - len(data) - head_bytes

        raw = list(self.fpga.read(ram_name, total_bytes, addr))
        if tail_bytes == 0:
            raw[head_bytes:] = list(data)
        else:
            raw[head_bytes:-tail_bytes] = list(data)

        self.fpga.write(ram_name, ''.join( raw ), addr)


    def read_block_bram(self,ram_name, block_size, byte_addr):
        """
        Read a large unpacked string of bytes from ram. No limitations of address or size, no need to be 32-bit bounded words.
        :param ram_name: Name of the BRAM to read
        :param block_size: The size in bytes of the block to read
        :param byte_addr: The address to start reading the data block
        """
        addr = (byte_addr//4)*4
        head_bytes = byte_addr % 4
        size = (head_bytes+block_size-1)//4 + 1
        total_bytes = size*4
        tail_bytes = total_bytes - block_size - head_bytes

        raw = list(self.fpga.read(ram_name, total_bytes, addr))
        if tail_bytes == 0:
            data = ''.join( raw[head_bytes:] )
        else:
            data = ''.join( raw[head_bytes:-tail_bytes] )

        return data




