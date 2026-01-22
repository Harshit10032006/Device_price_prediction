import pandas as pd 
from sqlalchemy import create_engine

# SQL SERVER CONNECTION
engine= create_engine( "mssql+pyodbc://@harshit\\SQLEXPRESS/DEVICES"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes")

# PHONE DATA PREPARATION
data=pd.read_csv('phone_price.csv')   
data.rename(columns={
    "Battery capacity": "BatteryCapacity",
    "Screen size": "ScreenSize",
    "RAM (MB)": "RAM_MB",
    "Internal storage (GB)": "InternalStorage_GB",
    "4G/LTE": "Has4G_LTE",
    "Wi-Fi": "HasWiFi"
}, inplace=True)
data.to_csv('phone_price.csv',index=False)

data.to_sql('Phones',engine,index=False)

# LAPTOP DATA PREPARATION

lap=pd.read_csv(r"C:\Users\kholi\datascience\Project Phones\laptop_price.csv")
lap.rename(columns={'Ram':'RAM_MB','Company':'Brand'},inplace=True)
lap.rename(columns={'Price_euros':'Price'},inplace=True)
lap.rename(columns={'Inches':'Screen size (inches)','Product':'Name'},inplace=True)

lap['RAM_MB']=lap['RAM_MB'].str.replace('GB',"")
lap['RAM_MB'] = pd.to_numeric(lap['RAM_MB'])   

lap['RAM_MB']=lap['RAM_MB']*1024
lap['Price']=lap['Price']*107.22
lap.drop(columns=['Unnamed: 16'], inplace=True)


columns=lap['ScreenResolution'].str.findall(r'\d+')
lap['Resolution x']=columns.str[0].astype('Int64')
lap['Resolution y']=columns.str[1].astype('Int64')

lap.drop('ScreenResolution',axis=1,inplace=True)
lap.to_csv('laptop_price.csv',index=False)

lap.to_sql('Laptop',engine,index=False)








