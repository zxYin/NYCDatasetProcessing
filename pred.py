
import numpy as np
from statsmodels.tools.eval_measures import rmse, meanabs
from statsmodels.tsa.arima_model import ARIMA

def HA_Method(x, y_ground):

    x_shape = x.shape
    y_shape = y_ground.shape

    total = np.append(x, y_ground, axis=0)
    pred = np.empty(y_ground.shape)

    for k in range(total.shape[-1]):
        if k % 10 == 0:
            print(k)
        for j in range(total[..., k].shape[-1]):
            result = np.empty((7, 24 * 6, total.shape[1], total.shape[2]))
            ## 最后一天不需要参与预测
            for i in range(total.shape[0] - 1):
                weekday = i // (24 * 6) % 7
                timeslot = i % (24 * 6)

                result[weekday, timeslot, j, k] += total[i, j, k]
                ## 当x都读入后，开始预测
                if i >= x_shape[0] - 1:
                    ## 预测下一天 需要+1
                    pred[i-x_shape[0]+1, j, k] = result[(weekday + 1) % 7, timeslot, j, k] / ((i//(24*6)+1) // 7)
    
    result_amount = y_shape[0] * y_shape[1] * y_shape[2]

    y_ground_array = y_ground.reshape((result_amount))
    pred_array = pred.reshape((result_amount))

    print(rmse(y_ground_array, pred_array), meanabs(y_ground_array, pred_array))

def ARIMA_Method(x, y_ground):

    x = x.reshape((x.shape[0], x.shape[1] * x.shape[2]))
    y_ground = y_ground.reshape((y_ground.shape[0], y_ground.shape[1] * y_ground.shape[2]))

    result = np.empty(y_ground.shape)
    
    errors = []
    for i in range(x.shape[-1]):
        x_piece = x[:, i]
        if i % 100 == 0:
            print(i)
        try:
            model = ARIMA(x_piece, order=(1, 0, 0)).fit(disp=0)
            y_pred = model.forecast(steps=y_ground.shape[0])
            result[:, i] = y_pred[0]
        except:
            errors.append(i)

    y_shape = y_ground.shape
    result_amount1 = y_shape[0] * y_shape[1]

    y_ground_array = y_ground.reshape((result_amount1))
    pred_array = result.reshape((result_amount1))

    print(rmse(y_ground_array, pred_array), meanabs(y_ground_array, pred_array))

    result = np.delete(result, errors, 0)
    y_ground = np.delete(y_ground, errors, 0)

    y_shape = y_ground.shape
    result_amount = y_shape[0] * y_shape[1]

    y_ground_array = y_ground.reshape((result_amount))
    pred_array = result.reshape((result_amount))

    print(rmse(y_ground_array, pred_array), meanabs(y_ground_array, pred_array))

vdata = np.load("./Bike_OD_Image.npz")['arr_0'].astype('float32')
vdata = vdata.reshape((13104, 256, 256))

vdata_train = vdata[0:8784]
vdata_test = vdata[8784:]

ARIMA_Method(vdata_train, vdata_test)
# HA_Method(vdata_train, vdata_test)