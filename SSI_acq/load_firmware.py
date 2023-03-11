from SPM import SPM
import time
import matplotlib.pyplot as plt

spm0 = SPM(ip='192.168.0.100',firmware='correlate_2020-07-06_1147.fpg')

print 'Loading Firmware'
spm0.reload_firmware()

print 'Arming!'
spm0.force_arm()

