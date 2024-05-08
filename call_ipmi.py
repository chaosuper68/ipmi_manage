
import os 
from datetime import datetime
import time 
import subprocess
from config import server_ips
import threading


cmd_commands = [
    'chassis power status',
    "chassis poh",
    "chassis restart_cause",
    "sel elist"
]

def write_ipmitools_cmd(ipmi_ip, account, password, output_dir, cmd, cnt):
        if cnt%5 != 0: # 每5分钟执行一次这些命令
            return ''

        if not os.path.exists(output_dir):
            print('create dir :{}'.format(output_dir))
            os.makedirs(output_dir)
        shell_command = f"ipmitool -I lanplus -H {ipmi_ip} -U {account} -P {password} {cmd}"
        out_name = cmd.replace(" ", "_")
        output_file = os.path.join(output_dir, out_name)
        # 执行shell命令并等待执行完成
        process = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        # 将命令结果写入文件
        if stdout:
            with open(output_file, 'w') as file:
                file.write(stdout)
                # if cmd == 'sel elist':
                #     command = f"tail -n 50 {output_file} > {output_file}"
                #     os.system(command)


def call_ipmitool(ip_config, save_dir='sensor_data', file_num_keep=20, time_interval = 60):
    """每30秒执行一下获取传感器数据合令
    """
    # 运行shell命令并将结果写入txt文件
    # 获取当前时间
    cnt = 0
    ipmi_ip = ip_config['ipmi_ip']
    account = ip_config['account']
    password = ip_config['password']
    host_name = ip_config['host_name']
    print('host_name: ', host_name)
    while True:
        now = datetime.now()
        # 格式化时间字符串为 YYYY-MM-DD HH:MM:SS 格式
        formatted_time = now.strftime('%Y-%m-%d %H:%M:%S')
        output_dir = f"{save_dir}/{host_name}"
        if not os.path.exists(output_dir):
            print('create dir :{}'.format(output_dir))
            os.makedirs(output_dir)

        for cmd in cmd_commands:
            write_ipmitools_cmd(ipmi_ip, account, password, output_dir+'/others', cmd, cnt)

        shell_command = f"ipmitool -I lanplus -H {ipmi_ip} -U {account} -P {password} sensor list"
        output_file = os.path.join(output_dir, formatted_time)

        # 执行shell命令并等待执行完成
        process = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        # 将命令结果写入文件
        if stdout:
            with open(output_file, 'w') as file:
                file.write(stdout)


            # print(f"Shell命令的结果已经写入到{output_file}文件中。")
            # 删除旧文件，保留最新的100个文件
            files = os.listdir(f"{save_dir}/{host_name}")
            files = [os.path.join(f"{save_dir}/{host_name}", i) for i in files if 'other' not in i ]
            files.sort(key=os.path.getctime)  # 按创建时间排序
            num_files = len(files)
            if num_files > file_num_keep:
                for file_to_delete in files[:num_files - file_num_keep]:
                    os.remove(file_to_delete)
                    # print(f"删除文件: {file_to_delete}")
            time.sleep(time_interval)
            cnt += 1
        else:
            print('call ipmi failed')



if __name__ == '__main__':
    threads = []
    for host_name, ipmi in server_ips.items():
        thread = threading.Thread(target=call_ipmitool, args=(ipmi,))
        threads.append(thread)

    # 启动线程
    for thread in threads:
        thread.start()

        # 等待线程结束
    for thread in threads:
        thread.join()

    # call_ipmitool(save_dir='sensor_data')