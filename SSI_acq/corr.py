from SPM import SPM
import time
import matplotlib.pyplot as plt
import numpy as np
import struct


spm = SPM(ip='192.168.0.100',firmware='correlate_2020-07-06_1147.fpg')

print("Setting gains prior to quantisation.")
shift = 4*np.ones(256)
packed_data = struct.pack('>256B', *list(shift) )
spm.write_block_bram("stage1_quantizer_shift",packed_data,0)

print("Selecting inputs for correlation.")
#spm.write_register('corr_A',1)
#spm.write_register('corr_B',5)
spm.set_inputs(0,2)


#signal_cross = spm.get_cross()
#signal_auto_a = spm.get_auto_a()
#signal_auto_b = spm.get_auto_b()
#print 10 * np.log10( np.abs(signal_cross[40]  ) )
#
#plt.cla()
#plt.plot( 10 * np.log10( np.abs(signal_cross) ) , label="Cross")
#plt.plot( 10 * np.log10( np.abs(signal_auto_a) ) , label="Auto A")
#plt.plot( 10 * np.log10( np.abs(signal_auto_b) ) , label="Auto B")
#plt.legend()
#plt.ylim([-90,10])
#plt.show()
#plt.pause( 1.0 )

#exit()

plt.ion()
while 1:
   # print '--- Input Power ---'
   # print 'Input 0: ' , spm.get_power(0)
   # print 'Input 1: ' , spm.get_power(1)
   # print 'Input 2: ' , spm.get_power(2)
   # print 'Input 3: ' , spm.get_power(3)
   # print 'Input 4: ' , spm.get_power(4)
   # print 'Input 5: ' , spm.get_power(5)
   # print '\n'


    #NBytes = (8+8)*256 # The RAM is in 64 bit chunks in this order [Real(Ch 0), Imag(Ch 0), Real(Ch 1), Imag(Ch 1),....]
    #data = np.array( struct.unpack(">512q", spm.read_block_bram('corr_data',NBytes,0) ) )
    #real = data[0::2] / float(2**22) / float(2**19)
    #imag = data[1::2] / float(2**22) / float(2**19)
    #signal = real + 1j* imag
    
    #tmp = signal*1

    #signal[0::2] = tmp[0:128]
    #signal[1::2] = tmp[128:]

    signal_cross = spm.get_cross()
    signal_auto_a = spm.get_auto_a()
    signal_auto_b = spm.get_auto_b()
    print 10 * np.log10( np.abs(signal_auto_a[40]  ) )

    plt.cla()
    plt.plot( 10 * np.log10( np.abs(signal_cross) ) , label="Cross")
    plt.plot( 10 * np.log10( np.abs(signal_auto_a) ) , label="Auto A")
    plt.plot( 10 * np.log10( np.abs(signal_auto_b) ) , label="Auto B")
    plt.legend()
    plt.ylim([-90,10])
    plt.show()
    plt.pause( 1.0 )

