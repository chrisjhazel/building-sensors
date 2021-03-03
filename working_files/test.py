#import getpass
#import datetime

#uploadTime = datetime.time(hour=6)
#currentTime = datetime.datetime.now()
#tomorrowTime = currentTime + datetime.timedelta(days=301)
#tomorrowTime = tomorrowTime.replace(hour=6, minute=0, second=0)

#difference = tomorrowTime - currentTime
#print(difference.total_seconds())
#currentTime.day
#print(uploadTime, currentTime, tomorrowTime)

naem = "sensor1__20201224"

counter = 0
for i in naem:
    counter+=1
print(counter)