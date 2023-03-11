from SNAP import SNAP
from netaddr.ip import IPAddress
from netaddr import EUI
import struct
import numpy as np

# ----------------- SPM --------------------
# - Basic Initialisation code
# - Makes use of new micro-blaze code - update static IP, etc.
# - edit configuration
# - set a beam and a track - auto calculate tracking parameters, return expected tracking error


class SPM(SNAP):

    def __init__(self,ip,firmware):
        """
        Signal Processing Module
        The SPM Class extends the generic SNAP class providing firmware specific functionality.
        """
        # ---- SPM Configuration -----
        clk_src = 'synth'
        adc_inputs = 6
        sampling_rate = 500
        # ---- call SNAP class init ----
        super(SPM,self).__init__(ip,firmware,clk_src=clk_src,adc_inputs=adc_inputs,sampling_rate=sampling_rate)

        # ---- SPM constants ----
        self.n_channels = 256
        self.max_channels = 24
        self.max_jobs = 512
        self.max_beams = 32


    # ---- Arming Mechanism ----
    def arm(self):
        # TODO: set start GPS time
        self.write_register('trigger_arm',1)

    def disarm(self):
        self.write_register('trigger_arm',0)
        self.write_register('trigger_force_trig',0)

    def force_arm(self):
        self.write_register('trigger_arm',1)
        self.write_register('trigger_force_trig',1)
        self.write_register('trigger_force_trig',0)

    # ---- UDP enable ----
        def set_udp_ip(self,ip='192.168.0.202'):
                packed = struct.pack(">4B", *list(IPAddress(ip).words) )
                self.fpga.transport.blindwrite("eth_0_ten_gbe", packed, offset=0x10)

        def get_udp_ip(self):
                packed = self.fpga.transport.read("eth_0_ten_gbe", 16384)
                data = list(struct.unpack('>16384B', packed))
                print (data[16:20])

        def get_arp(self):
                packed = self.fpga.transport.read("eth_0_ten_gbe", 0x1000, offset=0x3000)
                data = np.array(   list(struct.unpack('>4096B', packed ))   )
                arp = np.reshape( data , [512, 8]  )
                return arp

        def set_arp(self,ip,mac):
                arp = self.get_arp()
                arp[ip,2:] = mac
                packed = struct.pack(">4096B", *list(arp.ravel()) )
                self.fpga.transport.blindwrite("eth_0_ten_gbe", packed , offset=0x3000)

    def enable_udp(self):
        self.write_register('udp_enable',1)

    def disable_udp(self):
        self.write_register('udp_enable',0)

    # ---- input & channel dependent digital gains ----
    def clear_gains(self):
        for i in range(self.adc_inputs):
            self.set_gains(i,[1.0])

    def set_gains(self,input_id,gains):
        """
        Set the channel gains for a specific input.
        :param input_id: The input id to apply the gain to.
        :param gains: A list containing the gains to be applied. It's length must be equall to the number of channels. Optionally it can be of length 1 in which a single gain is applied to all channels.
        """
        assert (type(input_id) == int) & (input_id >= 0) & (input_id < self.adc_inputs) ,"Invalid input ID"
        assert (type(gains) == list), "Invalid input. Gains must be of type list"
        assert (len(gains) == 1) | (len(gains) == self.n_channels) ,"Invalid input. Gains must be of length 1 or " + str(self.n_channels)

        if len(gains) == 1:
            gains = [gains[0]]*self.n_channels

        gains = np.array(gains)
        for ch in range(self.n_channels):
            self.write_bram('gain_correction_gains', gains[ch]*float(2**8) ,data_width=2,addr=(ch*self.adc_inputs+input_id))

    def get_gains(self,input_id):
        """
        Get the gains for a specific input.
        :param input_id: The input id to apply the gain to.
        """
        assert (type(input_id) == int) & (input_id >= 0) & (input_id < self.adc_inputs) ,"Invalid input ID"

        gains = [0]*self.n_channels
        for ch in range(self.n_channels):
            gains[ch] = self.read_bram('gain_correction_gains',data_width=2,addr=(ch*self.adc_inputs+input_id)) / float(2**8)
        return gains


    # ---- Beam Control ----
    def clear_beams(self):
        # ---- clear beam coefficients ----
        packed_bytes = struct.pack('>'+str(4*self.max_beams)+'B', *([0]*4*self.max_beams) )
        self.write_block_bram('phase_correction_start_time',packed_bytes,0)
        packed_bytes = struct.pack('>'+str(4*self.max_beams*self.adc_inputs)+'B', *([0]*4*self.max_beams*self.adc_inputs) )
        self.write_block_bram('phase_correction_c0',packed_bytes,0)
        self.write_block_bram('phase_correction_c1',packed_bytes,0)
        self.write_block_bram('phase_correction_c2',packed_bytes,0)
        self.write_block_bram('phase_correction_c3',packed_bytes,0)

    def set_beams(self,beams={'id' : 0, 'start_time': 0, 'delays': [{}]}):
        # ---- next set all the beam coefficients ----
        self.clear_beams()
        for beam in beams:
            self.write_bram('phase_correction_start_time', beam['start_time'], data_width=4, addr=beam['id'] )
            input_id = 0
            for delay in beam['delays']:
                self.write_bram('phase_correction_c0', struct.unpack('>I',struct.pack('>f', delay['c0'] ))[0] , data_width=4, addr=self.adc_inputs*beam['id']+input_id )
                self.write_bram('phase_correction_c1', struct.unpack('>I',struct.pack('>f', delay['c1'] ))[0] , data_width=4, addr=self.adc_inputs*beam['id']+input_id )
                self.write_bram('phase_correction_c2', struct.unpack('>I',struct.pack('>f', delay['c2'] ))[0] , data_width=4, addr=self.adc_inputs*beam['id']+input_id )
                self.write_bram('phase_correction_c3', struct.unpack('>I',struct.pack('>f', delay['c3'] ))[0] , data_width=4, addr=self.adc_inputs*beam['id']+input_id )
                input_id += 1

    def get_beams(self):
        beams = []
        for beam_id in range(self.max_beams):
            T = self.read_bram('phase_correction_start_time', data_width=4, addr=beam_id )
            if T == 0:
                continue
            beams.append({'id':beam_id,'start_time':T,'delays':[0]*self.adc_inputs})
            for input_id in range(self.adc_inputs):
                beams['delays'][input_id] = { 	'c0' : self.read_bram('phase_correction_c0', data_width=4, addr=self.adc_inputs*beam_id+input_id ),
                                                'c1' : self.read_bram('phase_correction_c1', data_width=4, addr=self.adc_inputs*beam_id+input_id ),
                                                'c2' : self.read_bram('phase_correction_c2', data_width=4, addr=self.adc_inputs*beam_id+input_id ),
                                                'c3' : self.read_bram('phase_correction_c3', data_width=4, addr=self.adc_inputs*beam_id+input_id ) 
                                            }
        return beams

    # ---- Jobs Control ----
    def clear_jobs(self):
        # ---- clear buffer selector ----
        packed_bytes = struct.pack('>256B', *([0]*256) )
        self.write_block_bram('data_buffer_channel_config',packed_bytes,0)
        self.write_block_bram('data_buffer_dbl_buffer_control_channel_config',packed_bytes,0)
        # ---- clear job_control ----
        packed_bytes = struct.pack('>'+ str( 4*self.max_jobs ) +'B', *( [0]*4*self.max_jobs ) )
        self.write_block_bram('job_control_dest_ip', packed_bytes, 0)
        packed_bytes = struct.pack('>'+ str( 2*self.max_jobs ) +'B', *( [0]*2*self.max_jobs ) )
        self.write_block_bram('job_control_dest_port', packed_bytes, 0)
        packed_bytes = struct.pack('>'+ str( 8*self.max_jobs ) +'B', *( [0]*8*self.max_jobs ) )
        self.write_block_bram('job_control_jobs', packed_bytes, 0)

    def set_jobs(self,jobs):

        if len(jobs) > self.max_jobs:
            raise ValueError('The number of jobs cannot exceed ' + str(self.max_jobs) )

        utilised_channels = [job['channel'] for job in jobs] # get list of all requested channels
        utilised_channels = list(set(utilised_channels)) # remove duplicate channel entries
        if len(utilised_channels) > self.max_channels:
            raise ValueError('The total number of utilised channels cannot exceed ' + str(self.max_channels))

        self.clear_jobs()

        # ---- first set buffer selector ----
        for i in range(len(utilised_channels)):
            self.write_bram('data_buffer_channel_config', i*2+1 ,data_width=1, addr=utilised_channels[i] )
            self.write_bram('data_buffer_dbl_buffer_control_channel_config', i*2+1, data_width=1, addr=utilised_channels[i] )

        job_id = 0
        for job in jobs:

            if job['type'] == 0:
                # ---- voltage capture job ----
                self.write_bram('job_control_dest_ip', int(IPAddress( job['ip'] )), data_width=4, addr=job_id)
                self.write_bram('job_control_dest_port', int(job['port']), data_width=2, addr=job_id)
                words = [ 2**15 + job['input'] , job['rf_id'] ,job['channel'] , 0 ]
                self.write_block_bram( 'job_control_jobs' , struct.pack(">4H",*words) , 8*job_id)

            else :
                # ---- beam former job ----
                self.write_bram('job_control_dest_ip', int(IPAddress( job['ip'] )), data_width=4, addr=job_id)
                self.write_bram('job_control_dest_port', int(job['port']), data_width=2, addr=job_id)
                words = [ 2**15 + 2**12 + int(job['input_mask']) , job['beam_id'] ,job['channel'] , 0 ]
                self.write_block_bram( 'job_control_jobs' , struct.pack(">4H",*words) , 8*job_id)

            job_id += 1



    def get_jobs(self):
        pass



    def create_vc_job(self,input_id,rf_id,channel,ip,port):
        """
        Create a Voltage Capture Job object. All inputs are validated ensuring the validity of the job object.
        """
        assert (type(input_id) == int) & (input_id >= 0) & (input_id < self.adc_inputs) ,"Invalid input ID"
        assert (type(rf_id) == int), "RF ID must be an integer"
        assert (channel < self.n_channels) & (channel >= 0), "The channel id must exist within the possible range"
        assert (type(ip)==str), "The IP address should be provided in the form of a string"
        try:
            IPAddress(ip)
        except:
            raise ValueError('Invalid IP address')
        assert (type(port)==int) & (port >= 1024), "Custom port numbers should be greater than 1024"

        job = {'type' : 0}
        job['input'] = input_id
        job['rf_id'] = rf_id
        job['channel'] = channel
        job['ip'] = ip
        job['port'] = port

        return job


    def create_beam_job(self,input_mask,beam_id,channel,ip,port):
        """
        Create a Beam Job object. All inputs are validated ensuring the validity of the job object.
        """
        assert (type(beam_id) == int), "Beam ID must be an integer"
        assert (channel < self.n_channels) & (channel >= 0), "The channel id must exist within the possible range"
        assert (type(ip)==str), "The IP address should be provided in the form of a string"
        try:
            IPAddress(ip)
        except:
            raise ValueError('Invalid IP address')
        assert (type(port)==int) & (port >= 1024), "Custom UDP port numbers should be greater than 1024"

        job = {'type' : 1}
        job['input_mask'] = input_mask
        job['beam_id'] = beam_id
        job['channel'] = channel
        job['ip'] = ip
        job['port'] = port

        return job


    # ---- Static Network Interface Configuration ----
    def clear_static_netif(self):
        self.set_static_netif('0.0.0.0','0.0.0.0','0.0.0.0')

    def set_static_netif(self,ip,netmask,gateway):
        """
        Set the static network interface for m&c control
        Can only write to non-volatile memory in blocks of 0x10000 bytes. So we must read first, insert our data and write again.
        """
        SECTOR_START_ADDR = 0x800000 - 0x10000
        DATA_OFFSET = 0x10000 - 0x100
        DATA_SIZE = 0x100

        # ---- define ip, netmask and gateway ----
        IP = IPAddress(ip).words
        NM = IPAddress(netmask).words
        GW = IPAddress(gateway).words

        # ---- read sector and insert payload -----
        payload = [0]*DATA_SIZE
        payload[0:4]  = IP
        payload[4:8]  = NM
        payload[8:12] = GW
        sector = self.fpga.transport.read('/flash', 0x10000, offset=SECTOR_START_ADDR)
        data = sector[0:DATA_OFFSET] + struct.pack('>'+str(DATA_SIZE)+'B',*payload)

        # ---- Do the write operation ----
        old_timeout = self.fpga.transport.timeout
        self.fpga.transport.timeout = 1.5
        self.fpga.transport.blindwrite('/flash', data, offset=SECTOR_START_ADDR)
        self.fpga.transport.timeout = old_timeout

    def get_static_netif(self):
        START_ADDR = 0x800000 - 0x100
        DATA_SIZE = 0x100
        raw_data = self.fpga.transport.read('/flash', DATA_SIZE, offset=START_ADDR)
        data = list(struct.unpack('>'+str(DATA_SIZE)+'B',raw_data))
        data = map(str, data)
        netif = {
            'ip' :      IPAddress( '.'.join(data[0:4])  ),
            'netmask' : IPAddress( '.'.join(data[4:8])  ),
            'gateway' : IPAddress( '.'.join(data[8:12]) )
        }
        return netif


    # ---- Telemetry ----
    def set_inputs(self,a,b):
        self.write_register('input_select_A',a)
        self.write_register('input_select_B',b)

    def get_cross(self):
        NBytes = (8+8)*1024 # The RAM is in 64 bit chunks in this order [Real(Ch 0), Imag(Ch 0), Real(Ch 1), Imag(Ch 1),....]
        data = np.array( struct.unpack(">2048q", self.read_block_bram('cross_ab_data',NBytes,0) ) )
        real = data[0::2] / float(2**22) / float(2**19)
        imag = data[1::2] / float(2**22) / float(2**19)
        signal = real + 1j* imag
        return signal

    def get_auto_a(self):
        NBytes = (8)*1024 # The RAM is in 64 bit chunks in this order [Real(Ch 0), Imag(Ch 0), Real(Ch 1), Imag(Ch 1),....]
        data = np.array( struct.unpack(">1024q", self.read_block_bram('auto_a_data',NBytes,0) ) )
        signal = data / float(2**22) / float(2**19)
        return signal

    def get_auto_b(self):
        NBytes = (8)*1024 # The RAM is in 64 bit chunks in this order [Real(Ch 0), Imag(Ch 0), Real(Ch 1), Imag(Ch 1),....]
        data = np.array( struct.unpack(">1024q", self.read_block_bram('auto_b_data',NBytes,0) ) )
        signal = data / float(2**22) / float(2**19)
        return signal





