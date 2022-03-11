from bluepy import btle
import time

allDevices = []

for i in range(5):
        
    scanner = btle.Scanner()
    devices = scanner.scan(5)

    for dev in devices:
        if dev not in allDevices:
            allDevices.append(dev)
    
    time.sleep(10)

for dev in allDevices:
    if dev.connectable:
        print(dev.addr)
        for (adtype, desc, value) in dev.getScanData():
            if desc == "Complete Local Name":
                print(desc, value)