import psycopg2
import hashlib
import wmi
import subprocess
import socket
import tkinter as tk




# Настройка подключения к базе данных PostgreSQL
DB_HOST = 'localhost'  # Или IP адрес контейнера Docker
DB_PORT = '5432'  # Порт PostgreSQL
DB_NAME = 'postgres'
DB_USER = 'Admin1'
DB_PASSWORD = 'Power1983'


def hardware_monitor():

    # Путь к вашему .exe файлу
    path_to_exe = "C:\\Users\\alkos\\Downloads\\openhardwaremonitor-v0.9.6\\OpenHardwareMonitor\\OpenHardwareMonitor.exe"
    # Запуск .exe файла с правами администратора
    subprocess.run(["powershell", "-Command", f"Start-Process '{path_to_exe}' -Verb RunAs"])

def get_all_sensors():
    try:
        w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
        sensor_info = w.Sensor()
        sensors = {}
        for sensor in sensor_info:
            sensors[sensor.Name] = {
                "Type": sensor.SensorType,
                "Value": sensor.Value,
                "Min": sensor.Min,
                "Max": sensor.Max
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
def sensor_psname():
    all_sensors = get_all_sensors()
    computer_name = get_computer_name()

    data = {
        "ComputerName": computer_name,
        "Sensors": all_sensors
    }
    print(data)
    return data


# Функция для хэширования пароля (опционально)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Функция для аутентификации пользователя
def authenticate(username, password):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Хэширование пароля перед сравнением (если используется хэширование)
        hashed_password = hash_password(password)

        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, hashed_password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        return user

    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


# Пример функции, которая выполняется после успешного логина
def perform_task():
    # Пример выполнения какой-либо задачи


    all_sensors = get_all_sensors()
    computer_name = get_computer_name()

    data = {
        "ComputerName": computer_name,
        "Sensors": all_sensors
    }

    return data



# Функция для отправки результатов в базу данных
def send_result_to_db(user_id, result):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        cursor.execute("INSERT INTO results (user_id, result) VALUES (%s, %s)", (user_id, result))
        conn.commit()

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error connecting to the database: {e}")


def main(username, password):
    # Пример запроса логина и пароля у пользователя
    # username = input("Enter username: ")
    # password = input("Enter password: ")

    user = authenticate(username, password)

    if user:
        print(f"Login successful! Welcome, {username}.")


        # Выполнение задачи
        result = perform_task()
        print(result)

        # Отправка результата в базу данных
        send_result_to_db(user_id=user[0], result=result)
        print("Result has been sent to the database.")
    else:
        print("Login failed! Invalid username or password.")




def call_function():
    arg1 = entry1.get()
    arg2 = entry2.get()
    main(arg1, arg2)

def create_gui():
    global entry1, entry2
    root = tk.Tk()
    root.title("Пример GUI")

    call_button = tk.Button(root, text="Вызвать sensor_psname", command=sensor_psname)

    call_button.pack(pady=20)
    tk.Label(root, text="Аргумент 1:").pack(pady=5)
    entry1 = tk.Entry(root)
    entry1.pack(pady=5)

    tk.Label(root, text="Аргумент 2:").pack(pady=5)
    entry2 = tk.Entry(root)
    entry2.pack(pady=5)

    call_button = tk.Button(root, text="Вызвать функцию", command=call_function)
    call_button.pack(pady=20)

    root.mainloop()



p = create_gui()
if __name__ == "__main__":
    main()