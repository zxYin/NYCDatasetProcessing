import numpy as np; 
n = 1
fdata_total = None
vdata_total = None

for month in range (1, 13):
  filename = "2015-"+str(month).zfill(2)+"-"+str(60/n)+".npz"
  data = np.load(filename)
  if month == 1:
    fdata_total = data['fdata']
    vdata_total = data['vdata']
  else:
    fdata_total = np.vstack((fdata_total, data['fdata']))
    vdata_total = np.vstack((vdata_total, data['vdata']))

print(fdata_total.shape)
print(vdata_total.shape)

np.savez_compressed("taxi_od_60.npz", vdata = vdata_total, fdata = fdata_total)
print("finish")

# data1 = np.load("2015-01.npz")
# fdata1 = data1['fdata']
# vdata1 = data1['vdata']

# data2 = np.load("2015-02.npz")
# fdata2 = data2['fdata']
# vdata2 = data2['vdata']
# fdata2_slice = fdata2[:1344]
# vdata2_slice = vdata2[:1344]

# data3 = np.load("2015-03.npz")
# fdata3 = data3['fdata']
# vdata3 = data3['vdata']
# fdata3_slice = fdata3[:48]
# vdata3_slice = vdata3[:48]

# fdata_12 = np.vstack((fdata1, fdata2_slice))
# fdata = np.vstack((fdata_12, fdata3_slice))
# print(fdata.shape)

# vdata_12 = np.vstack((vdata1, vdata2_slice))
# vdata = np.vstack((vdata_12, vdata3_slice))
# print(vdata.shape)

# np.savez_compressed("od.npz", vdata = vdata, fdata = fdata)

# import numpy as np;
# data = np.load("od.npz")
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