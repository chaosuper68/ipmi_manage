## python call ipmi tools


import pandas as pd
import subprocess
import streamlit as st 
import requests
import pandas as pd 
import json 
import re 
import numpy as np 
from config import server_ips
import uuid


# st.markdown("4090 ipmi监控")


def get_sensors(backend_url, server_host):
    query_data = {'server_host': server_host}
    sensors = requests.post(backend_url, json=query_data)
    # print('sensors : ', sensors)
    response  = sensors.json()
    # print(response)
    the_create_time = response['time']
    sensor_data=response['result']
    # sensor_dict = json.loads(sensor_data)
    df = pd.DataFrame.from_dict(sensor_data)
    df.reset_index(drop=True, inplace=True)
    df.columns=['传感器', '读数', '单位', '状态', '0', '严重下限', '下限', '上限', '严重上限', '1']
    keep_names = ['传感器', '读数', '单位', '状态', '严重下限', '下限', '上限', '严重上限']

    df_clear = df[keep_names]
    return the_create_time, df_clear


sensor_map_dict = {
    'GPU1_PROC': 'GPU_1温度',
    'GPU4 Temp': 'GPU_4温度',
    'GPU3 Temp': 'GPU_3温度',
    'GPU1 Temp': 'GPU_1温度',
    'GPU2 Temp': 'GPU_2温度',
    'CPU Temp': 'CPU温度',
    'CPU_TEMP': 'CPU温度',
    'CPU0_TEMP': 'CPU0温度',
    'CPU0_DTS': 'CPU0核心温度',
    'MB_TEMP1': '主板温度一',
    'MB_TEMP2': '主板温度二',
    'MB_TEMP3': '主板温度三',
}

def get_key_sensors(df_sensors):
    regex = re.compile("^.{0,2}(CPU|GPU|MB|system|Peripheral).*(TEMP|DTS|PROC)", flags=re.IGNORECASE)

    def _str_match(x):
        if regex.findall(x):
            return True
        return False


    # 使用str.contains()方法筛选匹配正则表达式的行
    new_df = df_sensors[df_sensors['传感器'].map(_str_match)]
    new_df['传感器'] = new_df['传感器'].map(lambda x: x.strip())
    new_df['传感器'] = new_df['传感器'].map(lambda x:sensor_map_dict.get(x) if x in sensor_map_dict else x)
    new_df = new_df[~new_df['读数'].map(lambda x: True if 'na' in x else False)] 
    return new_df[['传感器', '读数']]

    # 打印新的DataFrame

def display_sensor(server_host):
    backend_url = 'http://localhost:9201/ipmi_sensors'
    create_time, df_sensors = get_sensors(backend_url, server_host)
    key_sensors = get_key_sensors(df_sensors)
    ipmi_ip = server_ips[server_host]['ipmi_ip']

    st.markdown('## 服务器：{}'.format(server_host))
    st.markdown('### IPMI IP：{}'.format(ipmi_ip))
    st.markdown('#### 监测时间：{}'.format(create_time))
    st.markdown("-----")
    st.markdown('###### 关键传感器')
    st.dataframe(key_sensors)
    st.markdown("-----")
    st.markdown('###### 全部传感器')
    st.dataframe(df_sensors)

    if st.button('刷新读数'):
        st.rerun()
    # 打印DataFrame

def display_power(server_host):
    backend_url = 'http://localhost:9201/power_status'
    query_data = {'server_host': server_host}
    power_status = requests.post(backend_url, json=query_data)
    response  = power_status.json()
    # print(response)
    power_on = response.get('power on', '')
    power_time = response.get('power time', '')
    last_restart = response.get('last_restart', '')
    st.markdown("-----")
    st.markdown('#### 电源状态')
    st.markdown("###### 开机状态：{}".format(power_on))
    st.markdown("###### 开机时长：{}".format(power_time))
    st.markdown("###### 上次重启原因：{}".format(last_restart))


def display_log(server_host):
    backend_url = 'http://localhost:9201/log_info'
    query_data = {'server_host': server_host}
    system_log = requests.post(backend_url, json=query_data)
    response  = system_log.json()
    df = pd.DataFrame.from_dict(response)
    df.reset_index(drop=True, inplace=True)
    st.markdown("-----")
    st.markdown('#### 系统日志')
    st.dataframe(df, width=800)

from config import server_ips

def power_widget(col, button_text, cmd, output_text, ipmi_ip, account, password):
    with col:
        power_button = st.button(button_text)
        if power_button:
                shell_command = f"ipmitool -I lanplus -H {ipmi_ip} -U {account} -P {password} {cmd}"
                # 执行shell命令并等待执行完成
                process = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                if stdout:
                    st.markdown(stdout)
                    st.markdown(output_text)
                else:
                    st.markdown(stderr)


def display_power_switch(server_host):
    ip_config = server_ips[server_host]
    ipmi_ip = ip_config['ipmi_ip']
    account = ip_config['account']
    password = ip_config['password']
    host_name = ip_config['host_name']
    print('host_name: ', host_name)
    admin_pass = 'Chaosuper_IPMI'
    if st.checkbox('电源管理', key=host_name):
        input_pass = st.text_input(label='请输入管理密码', type='password', key=host_name+'_1')
        if input_pass:
            if input_pass == admin_pass:
                st.markdown('----')
                c1, c2, c3, c4 = st.columns(4)
                # 关机
                power_widget(col=c1, button_text='关机', cmd='power off', output_text='已发送关机命令', ipmi_ip=ipmi_ip, account=account, password=password)
                power_widget(col=c2, button_text='开机', cmd='power on', output_text='已发送开机命令', ipmi_ip=ipmi_ip, account=account, password=password)
                power_widget(col=c3, button_text='重启', cmd='power reset', output_text='已发送重启命令', ipmi_ip=ipmi_ip, account=account, password=password)
                power_widget(col=c4, button_text='电源循环', cmd='power cycle', output_text='已发送电源循环命令', ipmi_ip=ipmi_ip, account=account, password=password)
            else:
                st.markdown('密码错误')
                st.stop()
        else:
            st.markdown('请输入密码')


