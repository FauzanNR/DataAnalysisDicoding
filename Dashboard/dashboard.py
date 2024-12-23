import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
# from streamlit.runtime.scriptrunner import add_script_run_ctx,get_script_run_ctx
# from subprocess import Popen

# ctx = get_script_run_ctx()

# process = Popen(['python','dashboard.py'])
# add_script_run_ctx(process,ctx)


st.header('E-Commerce Public Data Analysis Dashboard')


def data_preparation(df, start_date, end_date):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)
    df = df[(df['order_purchase_timestamp'] >= start_date) & (df['order_purchase_timestamp'] <= end_date)]
    return df


# Load the data
try:
    all_df = pd.read_csv('./Dashboard/all_data.csv')#path for streamlit cloud
except FileNotFoundError as e:
    print(e)
    print("changing file path")
    all_df = pd.read_csv('./all_data.csv')#path for local streamlit


start_date = st.date_input("Start Date", value=pd.to_datetime("2016-01-01"))
end_date = st.date_input("End Date", value=pd.to_datetime("2018-12-31"))

ready_df = data_preparation(all_df, start_date, end_date)

# State revenue
st.write("## State Revenue")
state_revenue = ready_df.groupby(by='customer_state')['payment_value'].sum().reset_index()
state_revenue = state_revenue.sort_values(by='payment_value', ascending=False)


plt.figure(figsize=(12, 6))
plt.barh(state_revenue['customer_state'].head(10), state_revenue['payment_value'].head(10), color='skyblue')
plt.text(state_revenue['payment_value'].values[0], state_revenue['customer_state'].values[0], f"{state_revenue['payment_value'].values[0]}")
plt.xlabel('Total Revenue')
plt.ylabel('Customer State')
plt.title('Top 10 Customer State by Total Revenue')

plt.gca().invert_yaxis()

st.pyplot(plt)


#Peak Purchasing Time
st.write("## Peak Purchasing Time (Hourly, Daily, and Quartal)")
ready_df['order_hour'] = ready_df['order_purchase_timestamp'].dt.hour
purchase_hour_trend = ready_df.groupby(by='order_hour').size().reset_index(name='order_count_in_hour')

order_count_in_hour_max = purchase_hour_trend['order_count_in_hour'].max()
peak_time = purchase_hour_trend.loc[purchase_hour_trend['order_count_in_hour'] == order_count_in_hour_max, ['order_hour', 'order_count_in_hour']]


plt.figure(figsize=(12, 6))
plt.plot(purchase_hour_trend['order_hour'], purchase_hour_trend['order_count_in_hour'])
plt.title('Hourly Purchase Trend')
plt.xlabel('Hours',size=15)
plt.scatter(peak_time['order_hour'], peak_time['order_count_in_hour'], s=15, label='Peak Purchase', color='red')
plt.text(peak_time['order_hour'], peak_time['order_count_in_hour'], f"{order_count_in_hour_max} orders at {peak_time['order_hour'].values[0]}:00", fontsize=10, color='red', ha='center', va='bottom')
plt.xticks(range(0,24))
plt.ylabel('Purchase Count')
st.pyplot(plt)


# Daily Revenue
ready_df['order_date'] = ready_df['order_purchase_timestamp'].dt.date
revenue_trend =ready_df.groupby(by=['order_id','order_date'])['payment_value'].sum().reset_index()
revenue_trend = revenue_trend.sort_values(by='order_date', ascending=True)
peak_revenue = revenue_trend['payment_value'].max()
peak_date = revenue_trend.loc[revenue_trend['payment_value']== peak_revenue, 'order_date'].values[0]



plt.figure(figsize=(12,6))
plt.plot(revenue_trend['order_date'], revenue_trend['payment_value'], label='Revenue', color = 'yellow')
plt.title('Revenue Trend in Daily Interval')
plt.xlabel('Date', size = 15)
plt.ylabel('Revenue', size=15)
plt.scatter(peak_date, peak_revenue, color='red', s=15)
plt.text(peak_date, peak_revenue, f"{peak_revenue} revenue on {peak_date}")
plt.legend()
st.pyplot(plt)

#Quartal Revenue
revenue_trend['order_date'] = pd.to_datetime(revenue_trend['order_date'])
revenue_quartal = revenue_trend.resample('Q', on='order_date').sum().reset_index()


plt.figure(figsize=(12, 6))
plt.bar(revenue_quartal['order_date'], revenue_quartal['payment_value'], color='skyblue', width=50)
plt.title("Revenue Trend In Quartal")
plt.xlabel('Date', size = 15)
plt.ylabel('Revenue', size = 15)
plt.legend()
st.pyplot(plt)

#Most Purchased Product
st.write("## Most Purchased Product")

most_purchased_product = all_df.groupby(by=[ 'product_category_name_english'])['order_id'].count().reset_index().sort_values(by='order_id', ascending=False)
most_purchased_product.columns = ['product_category_name_english', 'total_purchase']


plt.figure(figsize=(12, 6))
plt.barh(most_purchased_product['product_category_name_english'].head(10), most_purchased_product['total_purchase'].head(10), color='skyblue')
plt.text(most_purchased_product['total_purchase'].values[0], most_purchased_product['product_category_name_english'].values[0], f"{most_purchased_product['total_purchase'].values[0]}")
plt.ylabel('Product Category Name')
plt.xlabel('Customer Total Purchase')
plt.title('Top 10 Purchased Products')

plt.gca().invert_yaxis()
st.pyplot(plt)


#Seller Rank
st.write("## Seller Rank")
seller_order_delivered = all_df.loc[(all_df['order_status'] == 'delivered')]
top_ten_sellers = seller_order_delivered.groupby(by=['seller_id','seller_city','seller_state'])['order_id'].count().reset_index().sort_values(by='order_id', ascending=False)
top_ten_sellers.columns = ['seller_id','seller_city','seller_state','total_sales']

plt.figure(figsize=(12,6))
plt.barh(top_ten_sellers['seller_id'].head(10), top_ten_sellers['total_sales'].head(10), color='skyblue')
plt.text(top_ten_sellers['total_sales'].values[0], top_ten_sellers['seller_id'].values[0], f"{top_ten_sellers['total_sales'].values[0]}")
plt.ylabel('Seller ID')
plt.xlabel('Total Sales')
plt.gca().invert_yaxis()
st.pyplot(plt)

#Top ten seller origin
st.write("## Top Ten Seller City and State")
top_ten_seller_city = top_ten_sellers[['seller_id','seller_city','seller_state']].head(10).reset_index()
top_ten_seller_city.index = range(1, len(top_ten_seller_city)+1)
st.table(top_ten_seller_city)
