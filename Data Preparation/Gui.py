import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px

def data():
    engine=create_engine( "mssql+pyodbc://@harshit\\SQLEXPRESS/DEVICES"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes")

    return pd.read_sql('SELECT * FROM dbo.ml_devices',engine)

data=data()


st.set_page_config(page_title="Device Price Prediction",page_icon="🖥️",layout="wide")


st.title('Device Price Prediction System')
st.caption('An Machine Learning application for analyzing and estimating Devices Prices.')



tab_predic,tab_analysis=st.tabs(["Prediction","Analysis"])


with tab_analysis:
    st.subheader("Device Market Info:")

    device_type=st.selectbox("Select Device Type:",["Phone","Laptop"])
    device=data[data['device_type']==device_type]
    most_expensive =device["Price"].max()
    cheapest_=device['Price'].min()
    avg_price=device['Price'].mean()
    
    

    col1, col2, col3 = st.columns(3)

    col1.metric("Most Expensive Price",f"₹{int(most_expensive):,}")

    col2.metric( "Cheapest Price",f"₹{int(cheapest_):,}")
            
    col3.metric("Average Price",f"₹{int(avg_price):,}")
    st.caption("Prices are calculated from historical market data for the selected device type.")
    
    if st.button('Top Companies AVG'):

        brands_avg=(device.groupby('Brand')['Price'].mean().reset_index())
        if device_type=='Phone':
                top_brands=["Apple","Samsung","Google","OnePlus"]
        else :  
                top_brands=["Acer","Dell","HP","Asus"]
            
        top_data=brands_avg[brands_avg['Brand'].isin(top_brands)]
        others_data=brands_avg[~brands_avg['Brand'].isin(top_brands)]
 
        others_avg_price=others_data['Price'].mean()
        final = pd.concat([top_data,pd.DataFrame({"Brand": ["Others"],
                    "Price": [others_avg_price]})],ignore_index=True)
            
        fig = px.bar(final,x='Price',y='Brand',orientation='h',title=f'{device_type} Average Price by Brand',labels={'Price':'Average Price (₹)', 'Brand': ''},
                    color='Price',  
                    color_continuous_scale='Blues')
        fig.update_layout(height=400,showlegend=False,
            xaxis_tickformat='₹,.0f' 
        )
        st.plotly_chart(fig, use_container_width=True)
