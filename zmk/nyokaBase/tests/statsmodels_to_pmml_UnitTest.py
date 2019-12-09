import sys, os
import pandas as pd
import numpy as np
from statsmodels.tsa.base import tsa_model as tsa
from statsmodels.tsa import holtwinters as hw
from statsmodels.tsa.statespace import sarimax
from statsmodels.tsa.arima_model import ARIMA
import unittest
from nyoka import statsmodels_to_pmml


class TestMethods(unittest.TestCase):
    
    def getData1(self):
        # data with trend and seasonality present
        # no of international visitors in Australia
        data = [41.7275, 24.0418, 32.3281, 37.3287, 46.2132, 29.3463, 36.4829, 42.9777, 48.9015, 31.1802, 37.7179,
                40.4202, 51.2069, 31.8872, 40.9783, 43.7725, 55.5586, 33.8509, 42.0764, 45.6423, 59.7668, 35.1919,
                44.3197, 47.9137]
        index = pd.DatetimeIndex(start='2005', end='2010-Q4', freq='QS')
        ts_data = pd.Series(data, index)
        ts_data.index.name = 'datetime_index'
        ts_data.name = 'n_visitors'
        return ts_data
		
    def getData2(self):
		# data with trend but no seasonality
        # no. of annual passengers of air carriers registered in Australia
        data = [17.5534, 21.86, 23.8866, 26.9293, 26.8885, 28.8314, 30.0751, 30.9535, 30.1857, 31.5797, 32.5776,
                33.4774, 39.0216, 41.3864, 41.5966]
        index = pd.DatetimeIndex(start='1990', end='2005', freq='A')
        ts_data = pd.Series(data, index)
        ts_data.index.name = 'datetime_index'
        ts_data.name = 'n_passengers'
        return ts_data

    def getData3(self):
		# data with no trend and no seasonality
        # Oil production in Saudi Arabia
        data = [446.6565, 454.4733, 455.663, 423.6322, 456.2713, 440.5881, 425.3325, 485.1494, 506.0482, 526.792,
                514.2689, 494.211]
        index = pd.DatetimeIndex(start='1996', end='2008', freq='A')
        ts_data = pd.Series(data, index)
        ts_data.index.name = 'datetime_index'
        ts_data.name = 'oil_production'
        return ts_data
    
    def test_exponentialSmoothing_01(self):
        ts_data = self.getData1()        
        f_name='exponential_smoothing1.pmml'
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        damped=True, 
                                        seasonal='add', 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)
        
    def test_exponentialSmoothing_02(self):
        ts_data = self.getData1()        
        f_name='exponential_smoothing2.pmml'        
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        damped=False, 
                                        seasonal='add', 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_03(self):
        ts_data = self.getData1()        
        f_name='exponential_smoothing3.pmml'                
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        damped=True, 
                                        seasonal='mul', 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_04(self):
        ts_data = self.getData1()       
        f_name='exponential_smoothing4.pmml'
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        damped=False, 
                                        seasonal='mul', 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_05(self):
        ts_data = self.getData1()        
        f_name='exponential_smoothing5.pmml'        
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='mul', 
                                        damped=True, 
                                        seasonal='add', 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_06(self):
        ts_data = self.getData1()        
        f_name='exponential_smoothing6.pmml'                
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='mul', 
                                        damped=False, 
                                        seasonal='add', 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_07(self):
        ts_data = self.getData1()        
        f_name='exponential_smoothing7.pmml'                
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='mul', 
                                        damped=True, 
                                        seasonal='mul', 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)
        os.remove(f_name)

    def test_exponentialSmoothing_08(self):
        ts_data = self.getData1()        
        f_name='exponential_smoothing8.pmml'
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='mul', 
                                        damped=False, 
                                        seasonal='mul', 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)
        
    def test_exponentialSmoothing_09(self):
        ts_data = self.getData2()        
        f_name='exponential_smoothing9.pmml'        
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        damped=True, 
                                        seasonal=None, 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_10(self):
        ts_data = self.getData2()       
        f_name='exponential_smoothing10.pmml'               
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        damped=True, 
                                        seasonal=None, 
                                        seasonal_periods=None)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_11(self):
        ts_data = self.getData2()       
        f_name='exponential_smoothing11.pmml'                
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        damped=False, 
                                        seasonal=None, 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_12(self):
        ts_data = self.getData2()
        f_name='exponential_smoothing12.pmml'
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='add', 
                                        damped=False, 
                                        seasonal=None, 
                                        seasonal_periods=None)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_13(self):
        ts_data = self.getData2()       
        f_name='exponential_smoothing13.pmml'                
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='mul', 
                                        damped=True, 
                                        seasonal=None, 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_14(self):
        ts_data = self.getData2()        
        f_name='exponential_smoothing14.pmml'                
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='mul', 
                                        damped=True, 
                                        seasonal=None, 
                                        seasonal_periods=None)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_15(self):
        ts_data = self.getData2()  
        f_name='exponential_smoothing15.pmml'        
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='mul', 
                                        damped=False, 
                                        seasonal=None, 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)

    def test_exponentialSmoothing_16(self):
        ts_data = self.getData2()
        f_name='exponential_smoothing16.pmml'
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend='mul', 
                                        damped=False, 
                                        seasonal=None, 
                                        seasonal_periods=None)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)
        
    def test_exponentialSmoothing_17(self):
        ts_data = self.getData3()
        f_name='exponential_smoothing17.pmml'
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend=None, 
                                        damped=False, 
                                        seasonal=None, 
                                        seasonal_periods=None)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)
        
    def test_exponentialSmoothing_18(self):
        ts_data = self.getData3()
        f_name='exponential_smoothing18.pmml'
        
        model_obj = hw.ExponentialSmoothing(ts_data, 
                                        trend=None, 
                                        damped=False, 
                                        seasonal=None, 
                                        seasonal_periods=2)
        results_obj = model_obj.fit(optimized=True)
        
        statsmodels_to_pmml(ts_data, model_obj,results_obj, f_name)
        self.assertEqual(os.path.isfile(f_name),True)
    
    def test_non_seasonal_arima(self):

        fit_combin = [['c', 'css-mle', 'lbfgs'],['c', 'css-mle', 'nm'],['c', 'css-mle', 'bfgs'],['c', 'css-mle', 'powell'],['c', 'css-mle', 'cg'],
                      ['c', 'css-mle', 'ncg'],['c', 'mle', 'lbfgs'],['c', 'mle', 'nm'],['c', 'mle', 'bfgs'],['c', 'mle', 'powell'],['c', 'mle', 'cg'],
                      ['c', 'mle', 'ncg'],['c', 'css', 'lbfgs'],['c', 'css', 'nm'],['c', 'css', 'bfgs'],['c', 'css', 'powell'],['c', 'css', 'cg'],
                      ['c', 'css', 'ncg']]

        # no of cars sold
        data = [266,146,183,119,180,169,232,225,193,123,337,186,194,150,210,273,191,287,
                226,304,290,422,265,342,340,440,316,439,401,390,490,408,490,420,520,480]
        index = pd.DatetimeIndex(start='2016-01-01', end='2018-12-01', freq='MS')
        ts_data = pd.Series(data, index)
        ts_data.index.name = 'date_index'
        ts_data.name = 'cars_sold'

        c = 0
        for x in fit_combin:
            try:
                model = ARIMA(ts_data,order=(9, 2, 0))
                result = model.fit(trend = x[0], method = x[1], solver = x[2])
                try:
                    c = c + 1
                    file_name = 'non_seasonal_arima'+str(c)+'.pmml'
                    statsmodels_to_pmml(ts_data, model, result, file_name)
                except:
                    continue
                finally:
                    exported = os.path.isfile(file_name)
                    self.assertEqual(exported,True)
                    if(not exported):
                        break
            except:
                continue

    def test_seasonal_arima(self):

        model_combin = [[(3, 1, 1), (3, 1, 1, 12), 't', True, True, False, True, False, False, True, False], 
                        [(3, 1, 1), (3, 1, 1, 12), 't', True, True, False, False, False, False, False, False], 
                        [(3, 1, 1), (3, 1, 1, 12), 't', True, False, True, True, False, False, True, False], 
                        [(3, 1, 1), (3, 1, 1, 12), 't', True, False, True, False, False, False, False, False], 
                        [(3, 1, 1), (3, 1, 1, 12), 't', False, True, False, True, False, False, True, False], 
                        [(3, 1, 1), (3, 1, 1, 12), 't', False, True, False, False, False, False, False, False], 
                        [(3, 1, 1), (3, 1, 1, 12), 't', False, False, True, True, False, False, True, False], 
                        [(3, 1, 1), (3, 1, 1, 12), 't', False, False, True, False, False, False, False, False]]

        # no of cars sold
        data = [112, 118, 132, 129, 121, 135, 148, 148, 136, 119, 104, 118, 115, 126, 141, 135, 125, 149, 170, 170, 158, 133, 114, 140, 145, 150,
                178, 163, 172, 178, 199, 199, 184, 162, 146, 166, 171, 180, 193, 181, 183, 218, 230, 242, 209, 191, 172, 194, 196, 196, 236, 235,
                229, 243, 264, 272, 237, 211, 180, 201, 204, 188, 235, 227, 234, 264, 302, 293, 259, 229, 203, 229, 242, 233, 267, 269, 270, 315,
                364, 347, 312, 274, 237, 278, 284, 277, 317, 313, 318, 374, 413, 405, 355, 306, 271, 306, 315, 301, 356, 348, 355, 422, 465, 467,
                404, 347, 305, 336, 340, 318, 362, 348, 363, 435, 491, 505, 404, 359, 310, 337, 360, 342, 406, 396, 420, 472, 548, 559, 463, 407,
                362, 405, 417, 391, 419, 461, 472, 535, 622, 606, 508, 461, 390, 432]

        index = pd.DatetimeIndex(start='1949-01-01', end='1960-12-01', freq='MS')
        ts_data = pd.Series(data, index)
        ts_data.index.name = 'datetime_index'
        ts_data.name = 'n_passengers'

        c = 0
        for x in model_combin:
            try:
                model = sarimax.SARIMAX(endog = ts_data,
                                        exog = None,
                                        order = x[0],
                                        seasonal_order = x[1],
                                        trend = x[2],
                                        measurement_error = x[3], 
                                        time_varying_regression = x[4], 
                                        mle_regression = x[5], 
                                        simple_differencing = x[6], 
                                        enforce_stationarity = x[7], 
                                        enforce_invertibility = x[8], 
                                        hamilton_representation = x[9], 
                                        concentrate_scale = x[10])

                result = model.fit()
                try:
                    c = c + 1
                    file_name = 'seasonal_arima'+str(c)+'.pmml'
                    statsmodels_to_pmml(ts_data, model, result, file_name)
                except:
                    continue
                finally:
                    exported = os.path.isfile(file_name)
                    self.assertEqual(exported,True)
                    if(not exported):
                        break
            except:
                continue


if __name__=='__main__':
    unittest.main(warnings='ignore')
