import csv
from argparse import ArgumentParser

def get_args():
    # Get arguments passed through the command line terminal
    arg_parser = ArgumentParser(description="BLE IoT Sensor Demo")
    arg_parser.add_argument('mac_address', help="MAC address of device to connect")
    arg_parser.add_argument('project_name', help="The name of the project")
    arg_parser.add_argument('sensor_name', help="The name of the individual sensor")
    args = arg_parser.parse_args()

    #Save all of the arguments to a csv doc to call on later
    with open('sensor_directory.csv', 'a') as file:
        sensor_full_name = "{}_{}".format(args.project_name, args.sensor_name)
        writer = csv.DictWriter(file, fieldnames=['sensor_name', 'mac_address'])
        writer.writerow({'sensor_name': sensor_full_name, 'mac_address': args.mac_address})
        
    return args

def read_sensors():
    with open('sensor_directory.csv', 'r') as file:
        csv_read = csv.reader(file)
        for row in csv_read:
            print(row)

args = get_args()
print(args.mac_address)
print(args.project_name)
print(args.sensor_name)
