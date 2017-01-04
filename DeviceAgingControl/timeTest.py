from datetime import datetime
s1 = '20160531_10:33:26'
s2 = '20160601_00:15:49' # for example
FMT = '%Y%m%d_%H:%M:%S'
tdelta = datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)

print tdelta
