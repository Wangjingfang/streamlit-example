import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

# define functions
def style_negative(v, props=''):
    """ Style negative values in dataframe"""
    try:
        return props if v < 0 else None
    except:
        pass

def style_positive(v, props=''):
    """Style positive values in dataframe"""
    try:
        return props if v > 0 else None
    except:
        pass

def audience_simple(country):
    """ Show top countries"""
    if country == "US":
        return 'USA'
    elif country == "IN":
        return 'India'
    else:
        return 'Other'
# load data
@st.cache
def load_data():

    df_agg = pd.read_csv("aggreate_ByVideo.csv").iloc[1:,:]
    df_agg.columns = ['Video', 'Video title','Video publish time']
    df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'])
    df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
    df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
    df_agg['Engagement_ratio'] = (df_agg['Comments added'] + df_agg['Shares'] + df_agg['Dislikes'] + df_agg['Likes'])/ df_agg['subgained']
    df_agg['View / sub gained'] = df_agg['View']/df_agg['Subscribers gained']
    df_agg.sort_values('Video publish time', ascending= False, inplace= True)
    df_agg_sub = pd.read_csv("aggreate_By_Country.csv")
    df_comments = pd.read_csv("aggreate_Byvideo.csv")
    df_time = pd.read_csv("video_Performance_Over_Time.csv")
    df_time['Date'] = pd.to_datetime(df_time['Date'])

    return df_agg, df_agg_sub, df_comments, df_time

# create dataframes from the function
df_agg, df_agg_sub, df_comments, df_time = load_data()

# engineer data
df_agg_diff = df_agg.copy()
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months=12)
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median()

numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:, numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - median_agg).div(median_agg)

# merge daily data with publish data to get delta
df_time_diff = pd.merge(df_time, df_agg.loc[:,['Video', 'Video Publish time']], left_on= 'External Video ID', right_on=' xxx')
df_time_diff['days_published'] = (df_time_diff['Date'] - df_time_diff['Video publish time']).dt.days

# get last 12 months of data rather than all data
date_12mo = df_agg['Video publish time'].max() - pd.DateOffset(months=12)
df_time_diff_yr = df_time_diff[df_time_diff['Video publish time'] >= date_12mo]

# get daily view data(first 30), median & percentiles
views_days = pd.pivot_table(df_time_diff_yr, index='days_published', values='Views', aggfunc= [np.mean, np.median,lambda x: np.percentile(x, 80), lambda x: np.percentile(x, 20)]).reset_index()
views_days.columns = ['days_published', 'mean_views', 'median_views','80pct_views','20pct_views']
views_days = views_days[views_days['days_published'].between(0,30)]
views_cumulative = views_days.loc[:,['days_published', 'mean_views', 'median_views','80pct_views','20pct_views']]
views_cumulative.loc[:,['median_views','80pct_views','20pct_views']] = views_cumulative.loc[:,['median_views','80pct_views','20pct_views']].cumsum()
## what metrics will be relevant?
## Difference from baseline
## Percent change by video


# build dashboard
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics', 'Individual Video Analysis'))

# Total picture
if add_sidebar == 'Aggregate Metrics':
    # st.write('Agg')
    df_agg_metrics = df_agg[['Video publish time','View','Likes', 'Subscribers','Shares','comment added', 'RPM(USD)',
                             'Average % viewed', 'Avg_duration_sec','Engagement_ratio','Views/sub gained']]
    metric_date_6mo = df_agg_metrics['Vide publish time'].max() - pd.DateOffset(months=6)
    metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months=12)
    metric_medians6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo].median()
    metric_medians12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_12mo].median()

    # st.metric('View', metric_medians6mo['Views'], 500)
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]

    count = 0
    for i in metric_medians6mo.index:
        with columns[count]:
            delta = (metric_medians6mo[i] - metric_medians12mo[i])/metric_medians12mo[i]
            st.metric(label=i, value= round(metric_medians6mo[i],1), delta="{:.2%}".format(delta))
            count += 1
            if count >= 5:
                count = 0

    df_agg_diff['Publish_date'] = df_agg_diff['Video publish time'].apply(lambda x:x.date())
    df_agg_diff_final = df_agg_diff.loc[:,['Video title', 'Publish_date','View','Likes','Subscribe',
                                           'Avg_duration_sec','Engagement_ratio','Views/sub gained']]

    df_agg_numeric_lst = df_agg_diff_final.median().index.tolist()
    df_to_pct = {}
    for i in df_agg_numeric_lst:
        df_to_pct[i] = '{:.1%}'.format()

    st.dataframe(df_agg_diff_final.style.applymap(style_negative, props= 'color:red;').applymap(style_positive, props='color:green;').format(df_to_pct))
if add_sidebar == 'Individual Video Analysis':
    # st.write('Ind')
    videos = tuple(df_agg['Video title'])
    video_select = st.select_slider('Pick A Video:', videos)

    agg_filtered = df_agg[df_agg['Video title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select]
    agg_sub_filtered['Country'] = agg_sub_filtered['Country Code'].apply(audience_simple)
    agg_sub_filtered.sort_values('Is Subscribed', inplace=True)

    fig = px.bar(agg_sub_filtered, x='Views', y='Is Subscribed', color='Country', orientation='h')
    st.plotly_chart(fig)

    agg_time_filtered = df_time_diff[df_time_diff['Video Title'] == video_select]
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0,30)]
    first_30 = first_30.sort_values('days_published')

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['20pct_views'],
                              mode='Lines',
                              name = '20th percentile', line=dict(color='purple', dash='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['median_views'],
                              mode='Lines+markers',
                              name = '50th percentile', line=dict(color='black', dash='dash')))
    fig2.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['80pct_views'],
                              mode='Lines',
                              name = '80th percentile', line=dict(color='royalblue', dash='dash')))
    fig2.add_trace(go.Scatter(x=first_30['days_published'], y=first_30['Views'].cumsum(),
                              mode='Lines',
                              name='Current Video', line=dict(color='firebrick', width=8)))
    fig2.update_layout(title='View camparison first 30 days',
                       xaxis_title='Days Since Published',
                       yaxis_title='Cumulative views')

    st.plotly_chart(fig2)





