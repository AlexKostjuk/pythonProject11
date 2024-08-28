import hashlib
import time

import psycopg2
import wmi
import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
from datetime import timedelta
import tkinter as tk
import requests
import multiprocessing



datetime_madege = datetime.datetime.now()
datetime_db = datetime.datetime.now()
# running = False
running = multiprocessing.Value('b', False)


def authenticate(username, password):
    data = {'username': username, 'password': password}
    response = requests.post('http://localhost:8000/api/authenticate/', data=data)
    # print(response)
    result = response.json()
    if result['authenticated']:
        return result
    else:
        return None

def stop_loop():
    global running
    with running.get_lock():
        running.value = False

def call_function():
    arg1 = entry1.get()
    arg2 = entry2.get()
    # work(arg1, arg2)
    process = multiprocessing.Process(target=work, args=(arg1, arg2, running))
    process.start()


def create_gui():
    global entry1, entry2
    root = tk.Tk()
    root.title("Пример GUI")

    call_button = tk.Button(root, text="Вызвать sensor_psname", command=work)

    call_button.pack(pady=20)
    tk.Label(root, text="Аргумент 1:").pack(pady=5)
    entry1 = tk.Entry(root)
    entry1.pack(pady=5)

    tk.Label(root, text="Аргумент 2:").pack(pady=5)
    entry2 = tk.Entry(root)
    entry2.pack(pady=5)

    call_button = tk.Button(root, text="Вызвать функцию", command=call_function)
    call_button.pack(pady=20)

    stop_button = tk.Button(root, text="Остановить цикл", command=stop_loop)
    stop_button.pack(pady=20)

    root.mainloop()



def get_all_sensors():
    try:
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        sensor_info = w.Sensor()
        sensors = {}
        for sensor in sensor_info:
            sensors[sensor.Name] = {
                "Type": sensor.SensorType,
                "Value": sensor.Value,
                # "Min": sensor.Min,
                # "Max": sensor.Max
            }
        return sensors
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")
        return {}

def get_computer_name():
    try:
        return socket.gethostname()
    except Exception as e:
        print(f"Ошибка при получении имени компьютера: {e}")
        return "Unknown"



def compare_and_update_nested_dicts(main_dict1, main_dict2):
    updated_dict = main_dict1.copy()

    for key in updated_dict.keys():
        if key in main_dict2:
            nested_dict1 = updated_dict[key]
            nested_dict2 = main_dict2[key]

            for nested_key in nested_dict1.keys():
                if nested_key in nested_dict2 and nested_dict2[nested_key] > nested_dict1[nested_key]:
                    nested_dict1[nested_key] = nested_dict2[nested_key]

    return updated_dict

all_sensors = get_all_sensors()
computer_name = get_computer_name()
main_dict1 = get_all_sensors()

main_dict2 = {}



data = {
    "ComputerName": computer_name,
    "Sensors": all_sensors
}

# print(all_sensors)

def work(username, password, running):
    # global running
    user = authenticate(username, password)
    datetime_madege = datetime.datetime.now() - timedelta(minutes=6)
    datetime_db = datetime.datetime.now() #- timedelta(minutes=5)

    if user:
        with running.get_lock():
            running.value = True
        # running = True
        while running.value:

            main_dict1 = get_all_sensors()
            main_dict2= {}
            main_dict1 = compare_and_update_nested_dicts(main_dict1, main_dict2)
            # print(main_dict1)
            alarm = (main_dict1['CPU Core #4']['Value'])
            print(alarm)
            # print(datetime_madege)
            datetime_naw = datetime.datetime.now()
            if alarm > 50 and datetime_madege + timedelta(minutes=5) < datetime_naw :
                datetime_madege = datetime.datetime.now()
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                username = "alkost198333@gmail.com"
                password = "jkzv lbdn qlrw emsa"

                # Налаштування електронного листа
                from_email = "alkost198333@gmail.com"
                to_email = "alkost1983333@outlook.com"
                subject = "alarm Temp"
                body = f"temp CP = {alarm}."


                msg = MIMEMultipart()
                msg['From'] = from_email
                msg['To'] = to_email
                msg['Subject'] = subject


                msg.attach(MIMEText(body, 'plain'))


                try:

                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(username, password)


                    server.send_message(msg)
                    print("Лист успішно відправлений!")

                except Exception as e:
                    print(f"Помилка: {e}")

                finally:
                    server.quit()

            # if datetime_db  > datetime_naw:

            if datetime_db + timedelta(minutes=1) < datetime_naw:
                datetime_db = datetime.datetime.now()
                current_date = datetime_naw.date()
                current_time = datetime_naw.time()
                computer_name = get_computer_name()
                gpu_t = main_dict1['GPU Core']['Value']
                processor_t = main_dict1['CPU Core #4']['Value']
                processor_load = main_dict1['CPU Total']['Value']
                memori_load = main_dict1['Memory']['Value']
                user_id = user['user_id']

                data = {'date_comit': current_date, 'time_comit': current_time,
                        'terminal_name': computer_name, 'gpu_t': gpu_t,
                        'processor_t': processor_t, 'processor_load': round(processor_load),
                        'memori_load': round(memori_load),'user_id': int(user_id)}




                response = requests.post('http://localhost:8000/api/tobd/', data=data)
                print(response)
                result = response.json()
                if result['to_db']:
                    print(result)
                #     return result
                # else:
                #     return None



            time.sleep(2)

create_gui()