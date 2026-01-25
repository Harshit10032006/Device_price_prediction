from sklearn.pipeline import Pipeline
import joblib
from sqlalchemy import create_engine
import pandas as pd 
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder , StandardScaler
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.linear_model import LinearRegression

engine=create_engine( "mssql+pyodbc://@harshit\\SQLEXPRESS/DEVICES"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes")


MODEL_file='model.pkl'
PIPELINE_file='pipe.pkl'

#PIPELINE FUNCTION FOR NUMERICAL COLUMNS AND CAT_COLUMNS 
def build_pipeline(cat_col,num_col):
   
    num_pipeline=Pipeline([
                    ('scaling',StandardScaler())
                   ])
   
    cat_pipeline=Pipeline([
                    ('encoding',OneHotEncoder(handle_unknown='ignore'))
                ])

    full_pipeline=ColumnTransformer([('num',num_pipeline,num_col),
                                    ('cat',cat_pipeline,cat_col)])
    

    return full_pipeline



data=pd.read_sql('SELECT * FROM dbo.ml_devices',engine)

split=StratifiedShuffleSplit(n_splits=1,test_size=0.2,random_state=43) # GIVES INDEXES FOR TRAIN , TEST SPLITS
y=data['Price'].copy()
x=data.drop(columns=['device_id','Price','Name']).copy()


# Making the train,and test sets 
for train_idx,test_idx in split.split(x,x['device_type']):
    x_train=x.iloc[train_idx]
    x_test=x.iloc[test_idx]
    y_train=y.iloc[train_idx]
    y_test=y.iloc[test_idx]

num_col=['RAM_MB', 'Resolution x', 'Resolution y', 'screen_size_inches']
cat_col=['Brand', 'device_type']

pipeline=build_pipeline(cat_col,num_col)
data_final_train=pipeline.fit_transform(x_train)
data_final_test=pipeline.transform(x_test)


# Selecting best model 
models ={'Linear':LinearRegression(),
         'Random':RandomForestRegressor(),
         'Gradient': GradientBoostingRegressor()}
for name,model in models.items():
    model.fit(data_final_train,y_train)
    predic=model.predict(data_final_test)
    accu=mean_absolute_error(y_test,predic)
    print(name,accu)

# Building one final pipeline for preprocessing and model selection 
final_pipeline=Pipeline([('preprocessing',build_pipeline(cat_col,num_col)),
                         ('model',GradientBoostingRegressor(random_state=43))
                         ])


final_pipeline.fit(x_train,y_train)

joblib.dump(final_pipeline,'device_price_model.pkl')
