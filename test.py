import datetime

mydatetime = datetime.now() # or whatever value you want
twelvelater = mydatetime + datetime.timedelta(hours=12)
twelveearlier = mydatetime - datetime.timedelta(hours=12)

difference = abs(some_datetime_A - some_datetime_B)
# difference is now a timedelta object

# there are a couple of ways to do this comparision:
if difference > timedelta(minutes=1):
    print "Timestamps were more than a minute apart"

# or: 
if difference.total_seconds() > 60:
    print "Timestamps were more than a minute apart"