# 
import os 
from flask import Flask, jsonify, request
import pandas as pd 
 


app = Flask(__name__)

def get_file_name(server_host, folder_path = 'sensor_data'):
    data_dir = f"{folder_path}/{server_host}"
    file_names = os.listdir(data_dir)
    file_names = [os.path.join(data_dir, i) for i in file_names]
    file_names.sort(key=os.path.getctime)  # 按创建时间排序
    if file_names:
        file_name = file_names[-1]
    else:
        file_name = ''
    return file_name

        
    

@app.route('/ipmi_sensors', methods=['post'])
def get_sensors():
    server_host = request.json['server_host']
    file_name = get_file_name(server_host)
    data = pd.read_csv(file_name, header=None, sep='|')
    sensor_dict = data.to_dict()
    # print('file_name:{}'.format(file_name))
    the_time = file_name.split('/')[2]
    response = {
        'time':the_time,
        'result': sensor_dict
    }
    # print(sensor_dict)
    return jsonify(response)

def get_value_from(power_file):
    with open(power_file, encoding='utf-8') as f:
        _str = f.read()
    _str = _str.strip()
    # print(_str)
    _str_list = _str.split(":")
    if _str_list:
        return _str_list[-1]
    else:
        return ''
    

@app.route('/power_status', methods=['post'])
def get_power():
    server_host = request.json['server_host']
    file_name = f'sensor_data/{server_host}/others/chassis_power_status'
    power_on = get_value_from(file_name)

    file_name = f'sensor_data/{server_host}/others//chassis_poh'
    power_time = get_value_from(file_name)

    file_name = f'sensor_data/{server_host}//others/chassis_restart_cause'
    last_restart = get_value_from(file_name)

    power_readings = {
        'power on' : power_on,
        'power time': power_time,
        'last_restart': last_restart

    }
    # print(sensor_dict)
    return jsonify(power_readings)

@app.route('/log_info', methods=['post'])
def get_log():
    server_host = request.json['server_host']
    file_name = f'sensor_data/{server_host}/others/sel_elist'
    if os.path.exists(file_name):
        data = pd.read_csv(file_name, header=None, sep='@', on_bad_lines='skip')
        data = data.tail(100)
        log_dict = data.to_dict()
    else:
        log_dict = {'file_not_found': [True]}
    # print(sensor_dict)
    return jsonify(log_dict)



if __name__ == '__main__':
    app.run(port=9201)