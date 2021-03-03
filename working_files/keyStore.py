def addKeys():
    # Get keys for the data types
    #This is based on the sensor.ino file, confirm between files
    keys = [["TEMPERATURE", "°F"],
            ["HUMIDITY", "%"], 
            ["PRESSURE", "kPa"],
            ["LIGHT", "UNITS"],
            ["SOUND", "UNITS"]]

    #Create column key list to pass to SQL table
    columnKeys = []
    for key in keys:
        columnKeys.append(key[0])
    
    return columnKeys