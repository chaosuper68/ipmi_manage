

#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@时间    :2024/03/11 20:27:26
@作者    :jichaosun
'''

# 测试学术润色简单的webui
import streamlit as st 
from streamlit_option_menu import option_menu
import os 
from config import server_ips
from py_ipmi import display_sensor, display_power, display_log, display_power_switch



st.set_page_config(
        "算力云远程监控中心",
        os.path.join("imgs", "server.png"),
        initial_sidebar_state="expanded"
    )



with st.sidebar:
    st.image(
        os.path.join("imgs", "server.png"),
        use_column_width=True)
    st.caption(
        f"""<p align="right">Powered by IPMI</p>""",
        unsafe_allow_html=True,
    )


    options = list(server_ips)
    default_index = 0
    selected_page = option_menu(
        "算力机器选择",
        options=options,
        default_index=default_index,
    )

st.image(
        os.path.join("imgs", "ai_servers.jpg"),
        width=130)

if selected_page:

    display_sensor(selected_page)
    display_log(selected_page)
    display_power(selected_page)
    display_power_switch(selected_page)

# streamlit run main_page.py --server.port=8503
