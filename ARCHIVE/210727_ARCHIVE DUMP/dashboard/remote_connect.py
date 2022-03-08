#Script to connect to the remote database
def remote_connect():
    ####Remote database access details
    mac_remote_deats = r'/Users/chrishazel/Desktop/accessDetails.txt'
    rpi_remote_deats = None

    try:
        f = open(mac_remote_deats, 'r')
    except:
        f = open(rpi_remote_deats, 'r')

    remote_access = f.readlines()  # .replace("\n", "")
    f.close()

    return remote_access