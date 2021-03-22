import dBStore

projectName = "chrisoffice"

dbExists = dBStore.testDBExists(projectName)

if dbExists:
    tableList = dBStore.getTableList(projectName)
    print(tableList)

    for table in tableList:
        if "__archive" in table[0]:
            tableRename = dBStore.unrenameTable(projectName, table[0])

            if tableRename:
                print("Success")
    
    tableList = dBStore.getTableList(projectName)
    print(tableList)