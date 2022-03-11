from bluepy.btle import Scanner, DefaultDelegate
import time
import csv

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev and dev.connectable==True:
            for (adtype, desc, value) in dev.getScanData():
                if desc == "Complete Local Name":
                    print(dev.addr, desc, value)
                

                    with open('sensor_directory.csv', 'a') as file:
                        writer = csv.DictWriter(file, fieldnames=['sensor_name', 'mac_address'])
                        writer.writerow({'sensor_name': value, 'mac_address': dev.addr})
                
                

for i in range(1):

    scanner = Scanner().withDelegate(ScanDelegate())
    devices = scanner.scan(60.0, passive=True)

    time.sleep(5)


    for dev in devices:
        print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
            print("  %s = %s" % (desc, value))
            