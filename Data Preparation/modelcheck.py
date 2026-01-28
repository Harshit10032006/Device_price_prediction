import pandas as pd 
import joblib

model=joblib.load('device_price_model.pkl')


sample = pd.DataFrame([{
    'Brand': 'Apple',
    'device_type': 'Phone',
    'RAM_MB': 5000,
    'Resolution x': 1170,
    'Resolution y': 2532,
    'screen_size_inches': 6.1
}])

print(int(model.predict(sample)[0]))
