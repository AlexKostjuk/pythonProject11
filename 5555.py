import tkinter as tk
from datetime import datetime, timedelta
import requests
import wmi
import socket
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import multiprocessing
gue = True
running = multiprocessing.Value('b', False)

def authenticate(username, password):
    data = {'username': username, 'password': password}
    response = requests.post('http://localhost:8000/api/authenticate/', data=data)
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
    process = multiprocessing.Process(target=work, args=(arg1, arg2, running))
    process.start()

def create_gui():
    global gue
    if gue == True:
        gue = False
        global entry1, entry2
        root = tk.Tk()
        root.title("Пример GUI")

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

def work(username, password, running):
    user = authenticate(username, password)
    datetime_madege = datetime.now() - timedelta(minutes=6)
    datetime_db = datetime.now()

    if user:
        with running.get_lock():
            running.value = True
        while running.value:
            main_dict1 = get_all_sensors()
            main_dict2 = {}
            main_dict1 = compare_and_update_nested_dicts(main_dict1, main_dict2)
            alarm = main_dict1['CPU Core #4']['Value']
            print(alarm)
            datetime_now = datetime.now()
            if alarm > 50 and datetime_madege + timedelta(minutes=5) < datetime_now:
                datetime_madege = datetime.now()
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                email_username = "alkost198333@gmail.com"
                email_password = "jkzv lbdn qlrw emsa"

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
                    server.login(email_username, email_password)
                    server.send_message(msg)
                    print("Лист успішно відправлений!")
                except Exception as e:
                    print(f"Помилка: {e}")
                finally:
                    server.quit()

            if datetime_db + timedelta(minutes=1) < datetime_now:
                datetime_db = datetime.now()
                current_date = datetime_now.date()
                current_time = datetime_now.time()
                computer_name = get_computer_name()
                gpu_t = main_dict1['GPU Core']['Value']
                processor_t = main_dict1['CPU Core #4']['Value']
                processor_load = main_dict1['CPU Total']['Value']
                memori_load = main_dict1['Memory']['Value']
                user_id = user['user_id']

                data = {
                    'date_comit': current_date, 'time_comit': current_time,
                    'terminal_name': computer_name, 'gpu_t': gpu_t,
                    'processor_t': processor_t, 'processor_load': round(processor_load),
                    'memori_load': round(memori_load), 'user_id': int(user_id)
                }

                response = requests.post('http://localhost:8000/api/tobd/', data=data)
                print(response)
                result = response.json()
                if result['to_db']:
                    print(result)

            time.sleep(2)

create_gui()