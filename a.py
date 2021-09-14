import numpy as np; 
# n = 6
# fdata_total = None
# vdata_total = None

# for month in range (1, 13):
#   filename = "2015-"+str(month).zfill(2)+"-"+str(60/n)+"-bike.npz"
#   data = np.load(filename)
#   if month == 1:
#     fdata_total = data['fdata']
#     vdata_total = data['vdata']
#   else:
#     fdata_total = np.vstack((fdata_total, data['fdata']))
#     vdata_total = np.vstack((vdata_total, data['vdata']))

# print(fdata_total.shape)
# print(vdata_total.shape)

# np.savez_compressed("od_10_bike.npz", vdata = vdata_total, fdata = fdata_total)
# print("finish")

import numpy as np;
data = np.load("od_60_bike.npz")
print(data['fdata'].shape)
# fdata = data['fdata']
# time slot 0 ~ 2879
# origin width index 0 ~ 15
# origin height index 0 ~ 15
# destination width index 0 ~ 15
# destination height index 0 ~ 15
# passange count(0) OR trip count(1)

# vdata = data['vdata']
# time slot 0 ~ 2879
# width index 0 ~ 15
# height index 0 ~ 15
# start inside(0) OR end inside(1)
# passange count(0) OR trip count(1)