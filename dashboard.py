import os
import datetime
import calendar
import pandas as pd
import streamlit as st


class TGSRTC_dashboard:
    def __init__(self):
        self.folder_path = r"Monthwise Files"
        self.csv_files = os.listdir(self.folder_path)
        self.cities_list = [None] + pd.read_csv("Cities.csv")['PAX_CITIES'].unique().tolist()

    def read_file(self):
        try:
            start_month = self.start_date.month
            start_year = self.start_date.year
            end_month = self.end_date.month
            end_year = self.end_date.year
            files = []
            dfs = []
            while (start_year < end_year) or (start_year == end_year and start_month <= end_month):
                mon = calendar.month_abbr[start_month]
                file_path = os.path.join(self.folder_path, f"{mon}_{start_year}.csv")
                if os.path.exists(file_path):
                    files.append(file_path)
                if start_month == 12:
                    start_month = 1
                    start_year += 1
                else:
                    start_month += 1
            

            for file in files:
                df = pd.read_csv(file, low_memory=False)
                df.columns = df.columns.str.replace(' ', '')
                if self.bookings_type == 'OPRS':
                    df = df.dropna(subset=['MOBILE_NO'])
                elif self.bookings_type == 'NON OPRS':
                    df = df[df['MOBILE_NO'].isna()]
                df = df[['SERVICE_NO', 'SERVICE_START_DATE', 'PAX_BOARDING_CITY', 'PAX_DEST_CITY',
                        'PAX_BOARDING_POINT', 'PAX_DEST_POINT', 'NO_OF_PASSENGERS']]
                df['SERVICE_START_DATE'] = pd.to_datetime(df['SERVICE_START_DATE'], dayfirst=True, errors='coerce')
                df = df[(df['SERVICE_START_DATE'].dt.date >= self.start_date) & (df['SERVICE_START_DATE'].dt.date <= self.end_date)]
                dfs.append(df)
            if dfs:
                self.final_df = pd.concat(dfs,ignore_index=True)

        except Exception as e:
            st.error(f"ERROR reading file: {e}!")

    def dashboard_ui(self):
        page = None
        st.set_page_config(page_title='TGSRTC_OPRS_DASHBOARD', page_icon='LOGO.png')
        self.bookings_type = st.sidebar.selectbox(label="Bookings Type", options=['OPRS', 'NON OPRS', 'BOTH'])
        page = st.sidebar.radio("Navigate to", ["Month Wise Summary", "Stage Wise Summary"])
        col11, col12 = st.columns([1, 4])
        with col11:
            st.image('LOGO.png', width=80)
        with col12:
            st.title("TGSRTC DASHBOARD", anchor="https://www.tgsrtcbus.in/")

        if page == "Month Wise Summary":
            self.month_summary()
        
        elif page == "Stage Wise Summary":
            self.stage_summary()
        
    
    
    def month_summary(self):
        st.header("📊 Month Wise OPRS Summary")
        if self.dates():
            self.group_cols = None
            self.read_file()
            self.month_options()
            self.plot_graph()

    def dates(self):
        today = datetime.date.today()
        last_day_prev_month = today.replace(day=1) - datetime.timedelta(days=1)
        col1, col2 = st.columns(2)
        with col1:
            self.start_date = st.date_input("FROM DATE", value=None, key='from',
                                    min_value=datetime.date(2022, 4, 2),
                                    max_value=last_day_prev_month)
        with col2:
            if self.start_date:
                self.end_date = st.date_input("TO DATE", value=None, key='to',
                                    min_value=self.start_date,
                                    max_value=last_day_prev_month)

        if not self.start_date or not self.end_date:
            st.warning("Please select a valid date to proceed.")
            return False
        else:
            return True
        
    def month_options(self):
        dest_city = None
        org_point = None
        dest_point = None
        col21, col22 = st.columns(2)
        with col21:
            org_city = st.selectbox(label='BOARDING CITY', options=self.cities_list, placeholder='Choose Boarding City')
        with col22:
            if org_city:
                cities_list = self.final_df[(self.final_df['PAX_BOARDING_CITY'] == org_city)]
                cities_list = cities_list['PAX_DEST_CITY'].unique().tolist()
                dest_city = st.selectbox(label='DESTINATION CITY', options=cities_list, placeholder='Choose Destination City')
        if not org_city:
            st.warning("Enter Boarding City!")

        if org_city and dest_city:
            df = self.final_df.copy()
            df = df[(df['PAX_BOARDING_CITY'] == org_city) & (df['PAX_DEST_CITY'] == dest_city)]
            self.boarding_points = [None]+df['PAX_BOARDING_POINT'].dropna().unique().tolist()
            self.dest_points = [None]+df['PAX_DEST_POINT'].dropna().unique().tolist()
            col31, col32 = st.columns(2)
            with col31:
                org_point = st.selectbox(label='BOARDING POINT', options=self.boarding_points, placeholder='Choose Boarding Stage')
            with col32:
                dest_point = st.selectbox(label='DESTINATION POINT', options=self.dest_points, placeholder='Choose Destination Stage')

        c1,c2,c3,c4,c5 = st.columns(5)
        with c3:
            result_btn = st.button("🔍 ANALYZE")
        
        if result_btn:
            try:
                self.filtered1 = self.final_df.copy()

                if org_city: self.filtered1 = self.filtered1[self.filtered1['PAX_BOARDING_CITY'] == org_city]
                if dest_city: self.filtered1 = self.filtered1[self.filtered1['PAX_DEST_CITY'] == dest_city]
                if org_point: self.filtered1 = self.filtered1[self.filtered1['PAX_BOARDING_POINT'] == org_point]
                if dest_point: self.filtered1 = self.filtered1[self.filtered1['PAX_DEST_POINT'] == dest_point]
                        

                if self.filtered1.empty:
                    st.warning("No records found for the selected filters.")
                
                else:
                    self.group_cols = []
                    if org_city: self.group_cols.append('PAX_BOARDING_CITY')
                    if org_point: self.group_cols.append('PAX_BOARDING_POINT')
                    if dest_city: self.group_cols.append('PAX_DEST_CITY')
                    if dest_point: self.group_cols.append('PAX_DEST_POINT')

                    if self.group_cols:
                        PAX_TOTAL = self.filtered1.groupby(self.group_cols)[['NO_OF_PASSENGERS']].sum().reset_index()
                        st.write("Filtered Passenger Summary:")
                        st.dataframe(PAX_TOTAL)

                        st.write("Detailed Records:")
                        st.dataframe(self.filtered1)
                    else:
                        st.write("Filtered Passenger Summary:")
                        st.dataframe(self.filtered1)

            except Exception as e:
                st.error(f"Error: {e}")
    def plot_graph(self):
        if self.group_cols:
            group_cols2 = ['SERVICE_START_DATE'] + self.group_cols
            PAX_TREND = self.filtered1.groupby(group_cols2)[['NO_OF_PASSENGERS']].sum().reset_index()
            st.line_chart(data=PAX_TREND,x='SERVICE_START_DATE',y='NO_OF_PASSENGERS')


    
    def stage_summary(self):
        st.header("📊 Stage Wise OPRS Summary")
        if self.dates():
            self.read_file()
            self.stage_options()
    
    def stage_options(self):
        df = self.final_df.copy()
        dest_city = None
        col21, col22 = st.columns(2)
        with col21:
            org_city = st.selectbox(label='BOARDING_CITY', options=self.cities_list, placeholder='Choose Boarding City')
        with col22:
            if org_city:
                cities_list = self.final_df[(self.final_df['PAX_BOARDING_CITY'] == org_city)]
                cities_list = cities_list['PAX_DEST_CITY'].unique().tolist()
                dest_city = st.selectbox(label='DESTINATION CITY', options=cities_list, placeholder='Choose Destination City')
        if not org_city:
            st.write("Enter Boarding City!")

        

        if org_city and dest_city:
            df = df[(df['PAX_BOARDING_CITY'] == org_city) & (df['PAX_DEST_CITY'] == dest_city)]  
        elif org_city:
            df = df[(df['PAX_BOARDING_CITY'] == org_city)]
        elif dest_city:
            df = df[(df['PAX_DEST_CITY'] == dest_city)]
            
        services_list = [None]+df['SERVICE_NO'].unique().tolist()
        sno = st.selectbox(label='Service No',options=services_list, placeholder='Choose Service No')

        c1,c2,c3,c4,c5 = st.columns(5)
        with c3:
            result_btn = st.button("🔍 ANALYZE")
        
        if result_btn:
            try:
                self.filtered2 = self.final_df.copy()
                if sno:self.filtered2 = self.filtered2[self.filtered2['SERVICE_NO'] == sno]
                if org_city: self.filtered2 = self.filtered2[self.filtered2['PAX_BOARDING_CITY'] == org_city]
                if dest_city: self.filtered2 = self.filtered2[self.filtered2['PAX_DEST_CITY'] == dest_city]
                        

                if self.filtered2.empty:
                    st.warning("No records found for the selected filters.")
                
                else:
                    group_cols = []
                    if sno: group_cols.append('SERVICE_NO')
                    if org_city: group_cols.append('PAX_BOARDING_CITY')
                    if dest_city: group_cols.append('PAX_DEST_CITY')
                    
                    if group_cols:    
                        PAX_TOTAL = self.filtered2.groupby(group_cols)[['NO_OF_PASSENGERS']].sum().reset_index()
                        st.write("Filtered Passenger Summary:")
                        st.dataframe(PAX_TOTAL)

                        st.write("Detailed Records:")
                        st.dataframe(self.filtered2)

                        PAX_STAGE_DATA = self.filtered2.groupby(['PAX_BOARDING_POINT', 'PAX_DEST_POINT'])[['NO_OF_PASSENGERS']].sum().reset_index()
                        PAX_STAGE_DATA_PIVOT = PAX_STAGE_DATA.pivot(index='PAX_BOARDING_POINT', columns='PAX_DEST_POINT', values='NO_OF_PASSENGERS')
                        PAX_STAGE_DATA_PIVOT.index.name = 'PAX_BOARDING_POINT↓    PAX_DEST_POINT→'
                        st.write("Stagewise Data:")
                        st.dataframe(PAX_STAGE_DATA_PIVOT)
                    
                    else:
                        st.write("Filtered Passenger Summary:")
                        st.dataframe(self.filtered1)

            except Exception as e:
                st.error(f"Error: {e}")

        
if __name__ == "__main__":
    dashboard = TGSRTC_dashboard()
    dashboard.dashboard_ui()
