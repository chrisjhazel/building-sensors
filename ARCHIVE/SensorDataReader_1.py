import csv
import time
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

filename = "test_data_2"
csvFile = "{}.csv".format(filename)
keyFile = "{}_keys.csv".format(filename)

def keyReader(keyFile):
    #Read the CSV key file to determine the data types and values used
    #dataDict = {}
    dataType = []
    valueType = []

    with open(keyFile, newline='') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i != 0:
                dataType.append(row[0])
                valueType.append(row[1])
            else:
                continue
    return dataType, valueType


dataType, valueType = keyReader(keyFile)

df = pd.read_csv(csvFile)
df.columns = dataType



fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.plot(df["TEMPERATURE"], color="g")
ax1.grid(False)
ax2 = ax1.twinx()
ax2.plot(df["HUMIDITY"], color="r")
ax2.grid(False)
ax3 = ax1.twinx()
ax3.plot(df["PRESSURE"], color="b")
ax3.grid(False)

#sns.relplot(x = "TIME", y = "TEMPERATURE", kind = "line", data = df, ax=ax)
#sns.relplot(x="TIME", y="HUMIDITY", kind = "line", data=df, ax=ax)

#ax2 = ax.twinx()
#g.fig.autofmt_xdate()
plt.show()
