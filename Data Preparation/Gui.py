import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import plotly.express as px
import joblib
import numpy as np
def data():
    engine=create_engine( "mssql+pyodbc://@harshit\\SQLEXPRESS/DEVICES"
    "?driver=ODBC+Driver+17+for+SQL+Server"
    "&trusted_connection=yes")

    return pd.read_sql('SELECT * FROM dbo.ml_devices',engine)

data=data()


st.set_page_config(page_title="Device Price Prediction",page_icon="🖥️",layout="wide")

with st.sidebar:
    st.header("About")
    st.markdown("""
    **Device Price Prediction App**
    
    End-to-end ML system using SQL Server and Streamlit
    **Features:**
    
    - ML Powered Predictions 
    - Market analysis
    - Brand comparisons
    
    **Tech Stack:**
    - Python
    - Streamlit
    - SQL Server
    - Scikit-learn
    - Plotly
                """)
    st.divider()


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
        st.plotly_chart(fig)

    if st.button('Price Distribution'):
            if device_type=='Phone':
                bins=[0,5000,10000,20000,30000,40000,50000,75000,100000,np.inf]
                labels=['₹0-5K', '₹5K-10K', '₹10K-20K', '₹20K-30K', '₹30K-40K', '₹40K-50K', '₹50K-75K', '₹75K-1L', '₹1L+']
            else :
                 bins=[0,10000,20000,40000,60000,80000,100000,150000,200000,np.inf]
                 labels=['₹0-10K', '₹10K-20K', '₹20K-40K', '₹40K-60K', '₹60K-80K', '₹80K-1L', '₹1L-1.5L', '₹1.5L-2L', '₹2L+']
            
            dataa=data[data['device_type']==device_type]
            dataa['Price_Range']=pd.cut(dataa['Price'],bins=bins,labels=labels)
            price_counts = dataa['Price_Range'].value_counts().sort_index().reset_index()
            price_counts.columns = ['Price_Range', 'Count']
            chart=px.bar(price_counts, x='Price_Range',y='Count',
                title=f'{device_type} Price Distribution ',
                labels={'Price_Range': 'Price Range', 'Count': 'Number of Devices'},color='Count',color_continuous_scale='RdBu',
                text='Count')
            st.plotly_chart(chart)

with tab_predic:
        st.subheader("Device Price Prediction:")
        col1,col2,col3,col4=st.columns(4)
        
        with col1 :
            Device_type=st.selectbox("Device_Type",['Laptop','Phone'])
            brands=data[data['device_type']==Device_type]['Brand'].unique().tolist()
            selected_brand=st.selectbox("Brands",brands)
            
        with col2 :
              Screen_size=data['screen_size_inches'].unique().tolist()
              selected_screen_size=st.selectbox("Screen Size (Inches)",Screen_size)
              Ram=data['RAM_MB'].unique().tolist()
              selected_ram=st.selectbox('RAM(in MB)',Ram)
        with col3 :
              resx=st.slider("ResolutionX",4,3200,1440)
              resy=st.slider("ResolutionY",320,3840,2160)
        if st.button("Predict Price :"):
                model=joblib.load('device_price_model.pkl')
                prediction=pd.DataFrame([{'Brand':selected_brand,
                                      'device_type':Device_type,
                                      'RAM_MB':selected_ram,
                                      'Resolution x':resx,
                                      'Resolution y':resy,
                                      'screen_size_inches':selected_screen_size}])
                predicted_price= model.predict(prediction)[0]

                lower= predicted_price * 0.9
                upper = predicted_price * 1.1
                similar_devices =data[(data['device_type'] == Device_type) & (data['Brand'] == selected_brand)] 
                avg_brand_price =similar_devices['Price'].mean()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Minimum Expected", f"₹{int(lower):,}")
                with col2:
                    st.metric(" Predicted Price", f"₹{int(predicted_price):,}")
                with col3:
                    st.metric("Maximum Expected", f"₹{int(upper):,}")
                    
                st.caption(f"📱 Device: {selected_brand} {Device_type}, RAM: {selected_ram}MB  Screen: {selected_screen_size}\"")
                difference = predicted_price - avg_brand_price
                if difference > 0:
                    st.info(f"This prediction is ₹{int(abs(difference)):,} **above** the average {selected_brand} {Device_type} price (₹{int(avg_brand_price):,})")
                else:
                    st.info(f"This prediction is ₹{int(abs(difference)):,} **below** the average {selected_brand} {Device_type} price (₹{int(avg_brand_price):,})")
        st.subheader("Steps :")
        with st.expander("How to get accurate predictions"):
            st.markdown("""
            - Select the exact brand and device type
            - Choose specifications that match real devices
            - Higher RAM and resolution typically increase price
            - Screen size affects portability and price
            - Compare with market analysis tab for context
            """)
                    


        

            

