from crawler import mountain_crawler
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from db import read_config
from db import load_data
from db import load_data_apex
from db import load_data_apex2
from db import load_data_runtime
from db import load_data_runtime2
import folium
import pydeck as pdk
from streamlit_option_menu import option_menu
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import plotly.express as px
import json
from folium.plugins import MiniMap

mountain = load_data()
apex_df = load_data_apex()
apex_df2 = load_data_apex2()
runtime_df = load_data_runtime()
runtime_df2 = load_data_runtime2()

# 레이아웃 구성
st.set_page_config(layout="wide")
empty1,con1,empty2 = st.columns([0.4,1.0,0.4])

if not 'selectbox' in st.session_state:
    st.session_state['selectbox'] = ''

def page1():
    st.title('100대 명산 분포')

    col1, col2 = st.columns([3, 1.5])
    with col1:
        region_counts = mountain['region'].value_counts().reset_index()
        region_counts.columns = ['region', 'count']


        m = folium.Map(
        location=[mountain['lat'].mean(), mountain['lon'].mean()],
        zoom_start = 6.5
        )

        data = json.load(open('map.json', 'r', encoding='utf-8'))
        # st.write([data['features'][i]['properties']['CTP_KOR_NM'] for i in range(len(data['features']))])
        # st.write(region_counts['region'].unique())

        region_name = {'강원' : '강원도',
                    '경북' : '경상북도',
                    '경남' : '경상남도',
                    '전북' : '전라북도',
                    '서울/경기' : '경기도',
                    '전남' : '전라남도',
                    '충북' : '충청북도',
                    '충남' :  '충청남도',
                    '제주' : '제주특별자치도',
                    '서울' :  '서울특별시',
                    '세종' : '세종특별자치시',
                    '울산' : '울산광역시',
                    '광주' : '광주광역시',
                    '대전' : '대전광역시',
                    '부산' : '부산광역시',
                    '대구' : '대구광역시',
                    '인천' : '인천광역시'
        }

        new_name = pd.DataFrame({
                'region': ['서울', '세종', '울산', '광주', '대전', '부산', '대구', '인천'],
                'count': [15,6,21,13,6,17,21,15]
                    })
        region_counts = pd.concat([region_counts, new_name])
        

        region_counts['n_region'] = region_counts['region'].replace(region_name)

        # st.write(region_counts)

        folium.Choropleth(
            geo_data=data,
            data= region_counts,
            columns= [ 'n_region', 'count'],
            key_on= 'feature.properties.CTP_KOR_NM',
            fill_color= 'Reds',
            fill_opacity= 0.7,
            line_weight=0.3,
            line_color='Reds',
            line_opacity= 0.2,
        ).add_to(m)

        st_data = st_folium(m, width= 700, height= 800)

    
    with col2:
        # 지역별 산 분포 바차트
        region_counts = mountain['region'].value_counts().reset_index()
        region_counts.columns = ['region', 'count']
        fig = px.bar(region_counts, x='region', y='count',
                    title='지역별 산 분포',
                    text='count',
                    width=750, height=600,)

        st.plotly_chart(fig, use_container_width=True)


    region = st.selectbox('지역 선택', mountain['region'].unique(),key="selectbox1")
    apex_filtered = apex_df2[apex_df2['region'] == region]
    runtime_filtered = runtime_df2[runtime_df2['region'] == region]

    
    cols = st.columns(2)
    with cols[0]:
        # 전국 고도별 산 분포
        fig1 = px.pie(
            apex_df, names='category', values = 'total',
            hole= 0.3, title='전국 고도별 산 분포', labels = 'category',
            color_discrete_sequence=px.colors.sequential.Greens
        )
        st.plotly_chart(fig1)

        # 전국 소요시간별 산 분포
        fig2 = px.pie(
            runtime_df, names='category', values = 'total',
            hole = 0.3, title='전국 소요시간별 산 분포', labels= 'category',
            color_discrete_sequence=px.colors.sequential.Oranges
        )
        st.plotly_chart(fig2)

        
    with cols[1]:
        # 고도별 산 분포
        fig3 = px.bar(
            apex_filtered,
            x='total',
            y='category',
            orientation='h',
            text='total',
            title='고도별 산 분포',
            width=500, height=450,
            color_discrete_sequence=['green']
        )
        fig3.update_traces(textposition='outside')
        fig3.update_layout(yaxis=dict())  # categoryorder='total ascending'
        st.plotly_chart(fig3)

        # 소요시간별 산 분포
        fig4 = px.bar(
            runtime_filtered,
            x='total',
            y='category',
            orientation='h',
            text='total',
            title='소요시간별 산 분포',
            width=500, height=450,
            color_discrete_sequence=['orange']
        )
        fig4.update_traces(textposition='outside')
        fig4.update_layout(yaxis=dict())
        st.plotly_chart(fig4)
    
    
def page2():
    st.title('100대 명산 코스')
    
    cols = st.columns(2)
    with cols[0]:
        map_regions = st.selectbox('지역 선택', mountain['region'].unique(),key="selectbox2")
        region_filtered = mountain[mountain['region'] == map_regions]
    
    with cols[1]:
        m_select = st.selectbox('산 선택', region_filtered['name'], key="selectbox1")

    col1, col2 = st.columns([1.5, 1])
    with col1:
        map_df = region_filtered[['lat', 'lon', 'name', 'apex','run_time']]
        course_df = region_filtered[['lat', 'lon', 'name', 'apex', 'best_course', 'run_time', 'image',
                                    'course1', 'run_time1', 'course2', 'run_time2', 'course3', 'run_time3', 'course4', 'run_time4']]

        m = folium.Map(
        location=[region_filtered['lat'].mean(), region_filtered['lon'].mean()],
        zoom_start = 7.5
        )

        minimap = MiniMap(toggle_display=True,  position='bottomright',
                width=200, height=200, zoom_level_offset=-3) 
        minimap.add_to(m)

        marker_cluster = MarkerCluster().add_to(m)

        for _, row in map_df.iterrows():
            # 난이도 상(= 소요시간 )
            if row['apex'] > 1500:
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=folium.Popup(f"<b>고도</b>: {row['apex']}m 🔴 난이도 최상", max_width=100), 
                    tooltip=f"🏔️{row['name']}",
                    icon=folium.Icon(color="red")
                    
                ).add_to(marker_cluster)

            elif row['apex'] > 900:
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=folium.Popup(f"<b>고도</b>: {row['apex']}m 🟠 난이도 상", max_width=100), 
                    tooltip=f"🏔️{row['name']}",
                    icon=folium.Icon(color="orange")
                
                ).add_to(marker_cluster)

            elif row['apex'] > 600:
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=folium.Popup(f"<b>고도</b>: {row['apex']}m 🟢 난이도 중", max_width=100), 
                    tooltip=f"🏔️{row['name']}",
                    icon=folium.Icon(color="green")
                
                ).add_to(marker_cluster)

            else:
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=folium.Popup(f"<b>고도</b>: {row['apex']}m 🔵 난이도 하", max_width=100), 
                    tooltip=f"🏔️{row['name']}",
                    icon=folium.Icon(color="blue")
                
                ).add_to(marker_cluster)


        st_data = st_folium(m, width=500, height=600, 
                            returned_objects=['last_object_clicked'])


    with col2:
        if st_data['last_object_clicked'] is not None and st.session_state['selectbox'] == m_select:
            lat_clicked = st_data['last_object_clicked']['lat']
            lon_clicked = st_data['last_object_clicked']['lng']
            selected = course_df[(course_df['lat'] == lat_clicked) & (course_df['lon'] == lon_clicked)]
        else:
            st.session_state['selectbox'] = m_select
            selected = course_df[course_df['name'] == m_select]

        if not selected.empty:
            course_info = selected.iloc[0]
            st.write(f"● 산 : {course_info['name']}")
            st.write(f"● 고도 : {course_info['apex']}m")
            st.write(f"● 추천 코스 : {course_info.get('best_course', '정보 없음')}")
            st.write(f"● 소요시간 : {int(course_info.get('run_time', '정보 없음'))}분")
            st.markdown(f"![img]({course_info.get('image', '정보 없음' )})")



    
        # if st.checkbox('기타 코스 정보') :
        if st_data['last_object_clicked'] is not None and st.session_state['selectbox'] == m_select:
            lat_clicked = st_data['last_object_clicked']['lat']
            lon_clicked = st_data['last_object_clicked']['lng']
            selected = course_df[(course_df['lat'] == lat_clicked) & (course_df['lon'] == lon_clicked)]
        else:
                st.session_state['selectbox'] = m_select
                selected = course_df[course_df['name'] == m_select]

        if not selected.empty:
            if st.button('기타 코스 정보'):
                course_info = selected.iloc[0]
                for i in range(1, 5):
                    course = course_info.get(f'course{i}', '정보 없음')
                    run_time = course_info.get(f'run_time{i}', None)

                    if course is None or str(course).lower() == 'none':
                        course_display = '정보 없음'
                    else:
                        course_display = course

                    st.write(f"● 기타 코스{i} : {course_display}")

                    if isinstance(run_time, (int, float)) and run_time == run_time:
                        st.write(f"● 소요시간 : {int(run_time)}분")
                    else:
                        st.write("● 소요시간 : 정보 없음")


def page3():
    st.title('추가 정보')
    cols = st.columns(2)
    with cols[0]:
        map_regions = st.selectbox('지역 선택', mountain['region'].unique(),key="selectbox3")
        region_filtered = mountain[mountain['region'] == map_regions]
    with cols[1]:
        m_select = st.selectbox('산 선택', region_filtered['name'],key="selectbox2")

    # 산행포인트, 교통정보
    add = region_filtered[['name', 'point', 'traffic']]
    add_selected = add[add['name'] == m_select]

    if not add_selected.empty:
        course_info = add_selected.iloc[0]
        st.write(f"● 산 : {course_info['name']}")
        st.write(f"● 산행포인트 : {course_info['point']}")        
        st.write(f"● 교통정보 : {course_info['traffic']}")


        # 중복되는 산
        region_d = mountain.groupby('name')['region'].nunique()
        duplicated_names = region_d[region_d > 1].index
        d_mountain = mountain[mountain['name'].isin(duplicated_names)]

        # st.write(d_mountain)


# 사이드바
with st.sidebar:
    choose = option_menu("100대명산", ["분포", "코스", "추가 정보"],
                         icons=['bi bi-bar-chart', 'bi bi-geo','bi bi-dash-lg' ],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "black", "font-size": "20px"}, 
        "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#25462C"},
    }
    )
if choose == '분포' :
    page1()
    
elif choose == '코스':
    page2()

else:
    page3()