import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import warnings
import numpy as np

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Repeat Call Analysis!", page_icon=":airplane:", layout="wide")
# Path to the font file
font_path = '/Users/benedictadadson/Desktop/delta_dashboard/whitney-2-cufonfonts/whitneylight.otf'  # Update this path

# Convert the font file to a Base64 encoded string
with open(font_path, 'rb') as f:
    font_data = base64.b64encode(f.read()).decode()

# Path to the background image file
background_image_path = '/Users/benedictadadson/Desktop/delta_dashboard/bckgrnd_img_delta.jpeg'  # Update this path
with open(background_image_path, 'rb') as f:
    bg_image_data = base64.b64encode(f.read()).decode()

# CSS to inject custom font and style for the sidebar
custom_font_style = f"""
<style>
@font-face {{
    font-family: 'Whitney';
    src: url(data:font/otf;base64,{font_data}) format('opentype');
}}

html, body, h1, h2, h3, h4, h5, h6, p, div, span, a, li, input, button, .st-bb, .st-bv {{
    font-family: 'Whitney', sans-serif;
}}

.sidebar .sidebar-content {{
    background-image: url("data:image/png;base64,{bg_image_data}");
    background-size: cover;
    background-position: center;
}}
</style>
"""

custom_font_style += """
<style>
/* Attempt to target metric labels and values specifically */
.stMetricLabel, .stMetricValue {
    font-family: 'Whitney', sans-serif !important;
}

/* General attempt to override any text elements within Streamlit's metric widget */
[data-testid="metric-container"] * {
    font-family: 'Whitney', sans-serif !important;
}
</style>
"""

# Inject custom style at the top of the head tag
st.markdown(custom_font_style, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center; font-weight: bold;'>REPEAT CALL ANALYSIS</h2>", unsafe_allow_html=True)

st.markdown("""
    <style>
    .block-container{padding-top:1rem;}
    .sidebar .sidebar-content {width: 300px;}
    </style>
    """, unsafe_allow_html=True)

def load_data(file):
    df = pd.read_csv(file)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

with st.sidebar:
    fl = st.file_uploader("Upload initial data", type=["csv", "txt", "xlsx", "xls"], key="initial_upload")
    if fl is not None:
        st.session_state.df = load_data(fl)

    add_fl = st.file_uploader("Upload additional data", type=["csv", "txt", "xlsx", "xls"], key="additional_upload")
    if add_fl is not None:
        new_df = load_data(add_fl)
        st.session_state.df = pd.concat([st.session_state.df, new_df]).drop_duplicates().reset_index(drop=True)

    if not st.session_state.df.empty:
        df = st.session_state.df
        year_list = sorted(df['Date'].dt.year.unique(), reverse=True)
        selected_year = st.selectbox('Select a year', year_list, key="year_selector")
        df_selected_year = df[df['Date'].dt.year == selected_year]

        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        df_selected_year['Month'] = df_selected_year['Date'].dt.month.map(month_names)
        sorted_months = sorted(df_selected_year['Month'].unique(), key=lambda x: list(month_names.values()).index(x))
        selected_month = st.selectbox('Select a month', df_selected_year['Month'].unique(), key="month_selector")
        selected_month_num = list(month_names.keys())[list(month_names.values()).index(selected_month)]
        df_selected_month = df_selected_year[df_selected_year['Date'].dt.month == selected_month_num]

    tabs = st.radio("Navigation", ["Data Visualizations 1", "Data Visualizations 2"])

if not st.session_state.df.empty:
    if tabs == "Data Visualizations 1":
        avg_call_length = round(df['Call Length'].mean())
        avg_quoted_wait_time = round(df['Quoted_Wait_Time'].mean())

        # average call length for a selected month
        avg_call_length = round(df_selected_month['Call Length'].mean())
        total_specialists_selected_month = df_selected_month['Specialist_ID'].nunique()

        # display repeats per month
        total_repeats = len(df_selected_month[df_selected_month['Initial Repeat Flag'] == 1])
        total_non_repeats = len(df_selected_month[df_selected_month['Initial Repeat Flag'] == 0])
        repeat_percent = round((total_repeats / (total_repeats + total_non_repeats)) * 100)
        non_repeat_percent = round((total_non_repeats / (total_repeats + total_non_repeats)) * 100)

        total_repeats = df_selected_month['Initial Repeat Flag'].sum()

        sm_tier_repeats = df_selected_month[df_selected_month['Initial Repeat Flag'] == 1]['SM Tier'].value_counts()
        sm_tier_non_repeats = df_selected_month[df_selected_month['Initial Repeat Flag'] == 0]['SM Tier'].value_counts()

        col1, col2 = st.columns((2, 3))

        # Display metrics in the columns
        with col1:
            st.markdown("<h3 style='font-size:24px;'>Total Number of Repeat Calls</h3>", unsafe_allow_html=True)
            st.metric(label="", value=total_repeats)

            st.markdown("<h3 style='font-size:24px;'>Total No of Specialists</h3>", unsafe_allow_html=True)
            st.metric(label="", value=total_specialists_selected_month)

            st.markdown("<h3 style='font-size:24px;'>Avg Call Length (Mins)</h3>", unsafe_allow_html=True)
            st.metric(label="", value=avg_call_length)

            st.markdown("<h3 style='font-size:24px;'>Average Quoted Wait Time</h3>", unsafe_allow_html=True)
            st.metric(label="", value=avg_quoted_wait_time)

            total_repeats = df_selected_month['Initial Repeat Flag'].sum()
            total_non_repeats = len(df_selected_month) - total_repeats

            st.markdown(
                '<h4 ">Percentage of Repeat Calls vs Non Repeat Calls</h4>',
                unsafe_allow_html=True)
            fig = go.Figure(
                data=[go.Pie(
                    labels=['Repeat', 'Non-Repeat'],
                    values=[total_repeats, total_non_repeats],
                    hole=0.3,
                    marker=dict(colors=['red', 'green'])  # Set the colors of the pie chart slices
                )],
                layout=go.Layout(
                    title_font=dict(
                        family="Whitney, sans-serif",
                        # You may change 'Arial' to 'Whitney' if it's available in the environment
                        size=18,
                        color='black'
                    ),
                    margin=dict(l=0, r=0, t=0, b=0),  # Set left margin to 0
                    width=400,  # Set the width of the chart
                    height=300,  # Set the height of the chart
                )
            )
            st.plotly_chart(fig)

        with col2:
            # Time series analysis
            #st.write("Repeat Call Time Series Analysis")
            df_repeat_counts = df_selected_month.groupby('Date').size().reset_index(name='Repeat Calls')

            fig = px.line(df_repeat_counts, x='Date', y='Repeat Calls',
                          title=f'Repeat Calls Over Time for {selected_month}')

            # Update the title font and size
            fig.update_layout(
                title=dict(
                    text=f'Repeat Calls Over Time for {selected_month}',
                    x=0.5,  # Centers the title
                    xanchor='center',
                    font=dict(
                        family="Whitney, sans-serif",  # Replace with 'Whitney' if available
                        size=24,  # Adjust the title font size
                        color='black'
                    )
                )
            )

            # Optionally, if you want to change the color of the line:
            #fig.update_traces(line=dict(color='blue'))  # Sets the color of the line to navy
            st.markdown(f"<h4>Repeat Calls Over Time for {selected_month}</h4>",  unsafe_allow_html=True)
            st.plotly_chart(fig)


            # allow download functionality
            def download_data(df, file_name):
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # Convert dataframe to base64
                href = f'<a href="data:file/csv;base64,{b64}" download="{file_name}.csv">Download CSV File</a>'
                return href


            st.markdown(download_data(df_selected_month, 'time_series_data_per_month'), unsafe_allow_html=True)

            # top 5 intents

            df_repeats = df_selected_month[df_selected_month['Initial Repeat Flag'] == 1]

            # Now, get the top 5 intents from the filtered DataFrame
            top_intents = df_selected_month['Intent'].value_counts().head(5)

            # Convert the Series to a DataFrame
            top_intents_df = top_intents.reset_index()
            top_intents_df.columns = ['Intent', 'Count']

            # Create a horizontal bar chart
            fig = px.bar(top_intents_df, x='Count', y='Intent', orientation='h',
                         title='Top 5 Intents',
                         labels={'Count': 'Number of Calls', 'Intent': 'Intent'},
                         width=600, height=400,  # Adjust the width and height of the chart
                         color='Intent')  # Set color scheme

            fig.update_layout(
                title=dict(
                    text=f'Top 5 Intents for {selected_month}',
                    x=0.5,  # Centers the title
                    xanchor='center',
                    font=dict(
                        family="Whitney, sans-serif",  # Replace with 'Whitney' if available
                        size=24,  # Adjust the title font size
                        color='black'
                    )
                )
            )

            # Display the chart
            st.markdown(f"<h4>Top 5 Intents for {selected_month}</h4>", unsafe_allow_html=True)
            st.plotly_chart(fig)

    elif tabs == "Data Visualizations 2":
        # Example visualization code for "Data Visualizations 2" using df_selected_month:
        if not df_selected_month.empty:
            avg_call_length = round(df['Call Length'].mean())
            avg_quoted_wait_time = round(df['Quoted_Wait_Time'].mean())

            # average call length for a selected month
            avg_call_length = round(df_selected_month['Call Length'].mean())
            total_specialists_selected_month = df_selected_month['Specialist_ID'].nunique()

            # display repeats per month
            total_repeats = len(df_selected_month[df_selected_month['Initial Repeat Flag'] == 1])
            total_non_repeats = len(df_selected_month[df_selected_month['Initial Repeat Flag'] == 0])
            repeat_percent = round((total_repeats / (total_repeats + total_non_repeats)) * 100)
            non_repeat_percent = round((total_non_repeats / (total_repeats + total_non_repeats)) * 100)

            total_repeats = df_selected_month['Initial Repeat Flag'].sum()

            sm_tier_repeats = df_selected_month[df_selected_month['Initial Repeat Flag'] == 1]['SM Tier'].value_counts()
            sm_tier_non_repeats = df_selected_month[df_selected_month['Initial Repeat Flag'] == 0][
                'SM Tier'].value_counts()

            col1_tab2, col2_tab2 = st.columns(2)

            with col1_tab2:
                sm_tier_repeats = df_selected_month[df_selected_month['Initial Repeat Flag'] == 1][
                    'SM Tier'].value_counts()
                sm_tier_non_repeats = df_selected_month[df_selected_month['Initial Repeat Flag'] == 0][
                    'SM Tier'].value_counts()

                st.markdown('<h4>Repeat Calls by Tier</h4>', unsafe_allow_html=True)
                fig = go.Figure(data=[go.Pie(labels=sm_tier_repeats.index, values=sm_tier_repeats.values, hole=0.3)])
                st.plotly_chart(fig)

                # Repeats bar charts Age/Gender vs Non repeats bar charts Age/Gender
                age_bins = [0, 20, 40, 60, np.inf]
                labels = ['0-20', '21-40', '41-60', '61+']
                df_selected_month['Age Group'] = pd.cut(df_selected_month['Age'], bins=age_bins, labels=labels,
                                                        right=False)

                df_selected_month_repeats = df_selected_month[df_selected_month['Initial Repeat Flag'] == 1]
                # group by age group and gender, count repeats
                grouped_df = df_selected_month.groupby(['Age Group', 'Gender']).size().reset_index(
                    name='Number of Repeats')

                st.markdown('<h4>Repeat Calls by Age & Gender</h4>', unsafe_allow_html=True)
                fig = px.bar(grouped_df, x='Age Group', y='Number of Repeats', color='Gender',
                             labels={'Number of Repeats': 'Number of Repeats', 'Age Group': 'Age Group'})
                fig.update_layout(height=400)  # Adjust height as needed
                st.plotly_chart(fig, use_container_width=True)

            with col2_tab2:
                # Msg Within 12 Hrs vs Initial Repeat Flag
                st.markdown("<h4>Msg Within 12 Hrs vs Initial Repeat Flag</h4>", unsafe_allow_html=True)
                msg_within_12_hrs_chart = px.histogram(df_selected_month, x='Msg Within 12 Hrs',
                                                       color='Initial Repeat Flag',
                                                       barmode='group',
                                                       labels={'count': 'Count', 'variable': 'Msg Within 12 Hrs'})
                msg_within_12_hrs_chart.update_layout(height=400, width=700)
                st.plotly_chart(msg_within_12_hrs_chart)

                # Shift vs Initial Repeat Flag
                st.markdown("<h3>Shift vs Initial Repeat Flag</h3>", unsafe_allow_html=True)

                # Preprocess the data to create grouped bars
                df_grouped_shift = df_selected_month.groupby(['Shift', 'Initial Repeat Flag']).size().unstack(
                    fill_value=0)

                # Create a stacked horizontal bar chart
                shift_chart = px.bar(df_grouped_shift, orientation='h',
                                     labels={'value': 'Count', 'Shift': 'Shift', 'variable': 'Initial Repeat Flag'},
                                     color_discrete_map={'0': 'blue', '1': 'red'})

                # Update the vertical axis to show only the values 1, 2, and 3
                shift_chart.update_yaxes(tickvals=[1, 2, 3])

                shift_chart.update_layout(height=450)
                st.plotly_chart(shift_chart)
        else:
            st.write("No data available for the selected month and year.")
else:
    st.warning("Please upload data to proceed.")
