# import library
import pandas as pd
import altair as alt
import streamlit as st
import millify as mfy
from pathlib import Path # untuk path
# sns.set(style='dark')

# setting the page
st.set_page_config(
    page_title = "Bike Sharing App",
    page_icon = "bike-icon.jpg",
    layout = "wide",
    initial_sidebar_state = "expanded",
    menu_items = {
        "Get Help": "https://github.com/",
        "Report a bug": "https://github.com/",
        "About": "This is a dashboard of Bike Sharing Data"
    }
)

# persiapan dataframe yang dibutuhkan
# last hour
def create_last_hour_data(df):
    last_hour_data = df.groupby(by=["date", "hour"], observed=False).agg({
        "casual": "sum",
        "registered": "sum",
        "count": "sum"
    })
    last_hour_data = last_hour_data.sort_values(by=["date", "hour"], ascending=False)
    last_hour_data = last_hour_data.reset_index().head(2)
    return last_hour_data

# last day
def create_last_day_data(df):
    last_day_data = df.groupby(by="date", observed=False).agg({
        "casual": "sum",
        "registered": "sum",
        "count": "sum"
    })
    last_day_data = last_day_data.sort_values(by="date", ascending=False)
    last_day_data = last_day_data.reset_index().head(2)
    return last_day_data

# last month
def create_last_month_data(df):
    last_month_data = df.groupby(by=["year", "month"], observed=False).agg({
        "casual": "sum",
        "registered": "sum",
        "count": "sum"
    })
    last_month_data = last_month_data.sort_values(by=["year", "month"], ascending=False)
    last_month_data = last_month_data.head(2).reset_index()
    return last_month_data

# last total
def create_last_total_data(df):
    last_total_data = hour_df.agg({
        "casual": "sum",
        "registered": "sum",
        "count": "sum"
    })
    last_total_data = last_total_data.reset_index()
    last_total_data = last_total_data.rename(columns={
        "index": "user",
        0: "total"
    })
    return last_total_data

# gathering data/setting up the data
day_df = pd.read_csv(Path(__file__).parents[1] / 'data/day_data.csv', sep=",")
hour_df = pd.read_csv(Path(__file__).parents[1] / 'data/hour_data.csv', sep=",")

min_date = day_df["date"].min()
max_date = day_df["date"].max()

# ----------sidebar----------
with st.sidebar:
    st.sidebar.title("Bike Share Dashboard")
    # tambahkan logo
    st.image(Path(__file__).parents[1] / "data/bike-icon.jpg", width=40)

    # mengambil start_date & end_date dari date input
    sidebar_set1 = st.date_input(
        label='Pilih rentang waktu:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    try:
        start_date, end_date = sidebar_set1
    except ValueError:
        st.error("Anda harus memasukkan tanggal awal dan akhir")
        st.stop()

    # tambahkan filter weather atau season
    opsi_kategori = {
        "Cuaca": "weathersit",
        "Musim": "season"
    }

    sidebar_set2_label = st.sidebar.selectbox("Pilih kategori:", list(opsi_kategori.keys()))
    sidebar_set2 = opsi_kategori[sidebar_set2_label]  

# data filter
trend_data = day_df[(day_df["date"] >= str(start_date)) & (day_df["date"] <= str(end_date))]

# pemanggilan fungsi data
last_hour_data = create_last_hour_data(hour_df)
last_day_data = create_last_day_data(hour_df)
last_month_data = create_last_month_data(hour_df)
last_total_data = create_last_total_data(hour_df)

# ----------section 1----------
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("Hourly")
    last_hour = int(last_hour_data.loc[0, "count"])
    last_2hour = int(last_hour_data.loc[1, "count"])
    # st.metric("Last total users", value=last_hour_data["casual"])
    # st.metric("Last total users", value=last_hour_data["registered"])
    st.metric("Last total users", value=mfy.millify(last_hour), delta=mfy.millify((last_hour-last_2hour)))

with col2:
    st.subheader("Daily")
    last_day = int(last_day_data.loc[0, "count"])
    last_2day = int(last_day_data.loc[1, "count"])
    # st.metric("Last casual users", value=last_day_data["casual"])
    # st.metric("Last registered users", value=last_day_data["registered"])
    st.metric("Last total users", value=mfy.millify(last_day), delta=mfy.millify((last_day-last_2day)))

with col3:
    st.subheader("Monthly")
    last_month = int(last_month_data.loc[0, "count"])
    last_2month = int(last_month_data.loc[1, "count"])
    # st.metric("Last casual users", value=last_month_data["casual"])
    # st.metric("Last registered users", value=last_month_data["registered"])
    st.metric("Last total users", value=mfy.millify(last_month), delta=mfy.millify((last_month-last_2month)))

with col4:
    st.subheader("Total")
    # st.metric("Total casual users", value=last_total_data["total"][0])
    # st.metric("Total registered users", value=last_total_data["total"][1])
    st.metric("Total users", value=mfy.millify(last_total_data["total"][2]))

st.divider()

# ----------section 2----------
col1, col2 = st.columns([3,1])
with col1:
    st.subheader("Trend Peminjaman Sepeda")
    trend_chart = alt.Chart(trend_data).mark_line(point=True).encode(
        x=alt.X('date:T', title='Tanggal'),
        y=alt.Y('count:Q', title='Jumlah Peminjaman'),
        tooltip=['date:T', 'count:Q']
    ).properties(width=800, height=400)
    st.altair_chart(trend_chart, use_container_width=True)

    # section of section2
    st.subheader("About")
    st.write("Dataset ini tentang Bike-Sharing, diperoleh dari UC Irvine Machine Learning Repository, tautannya: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset")

with col2:
    st.subheader("Busy hours")
    hours_chart = alt.Chart(hour_df).mark_bar().encode(
        y=alt.Y('hour:O', title='Jam', sort=alt.SortField(field='hour', order='ascending'), axis=alt.Axis(values=list(range(24)))),
        x=alt.X('count:Q', title='Peminjaman'),
        tooltip=[alt.Tooltip('hour:O', title='Jam'), alt.Tooltip('count:Q', title='Rata-rata Peminjaman')]
    ).properties(
        width=600,
        height=600
    )
    st.altair_chart(hours_chart, use_container_width=True)

st.divider()

# ----------section 3----------
st.subheader(f"Users by {sidebar_set2_label}")

col1, col2 = st.columns(2)
with col1:
    st.text("Casual users")
    casual_chart = alt.Chart(day_df).mark_bar().encode(
        x=alt.X(f'{sidebar_set2}:N', title=sidebar_set2_label),
        y=alt.Y('casual:Q', title="Peminjaman"),
        tooltip=[
            alt.Tooltip(f'{sidebar_set2}:N', title=sidebar_set2_label),
            alt.Tooltip('casual:Q', title="Peminjaman Casual")
        ]
    )
    st.altair_chart(casual_chart, use_container_width=True)

with col2:
    st.text("Registered users")
    registered_chart = alt.Chart(day_df).mark_bar().encode(
        x=alt.X(f'{sidebar_set2}:N', title=sidebar_set2_label),
        y=alt.Y('registered:Q', title="Peminjaman"),
        tooltip=[
            alt.Tooltip(f'{sidebar_set2}:N', title=sidebar_set2_label),
            alt.Tooltip('registered:Q', title="Peminjaman Registered")
        ]
    )
    st.altair_chart(registered_chart, use_container_width=True)

st.divider()
