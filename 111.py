import wmi

def get_cpu_temperature():
    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
    temperature_info = w.Sensor()
    temperatures = {}
    for sensor in temperature_info:
        if sensor.SensorType == u'Temperature':
            temperatures[sensor.Name] = sensor.Value
    return temperatures

cpu_temperatures = get_cpu_temperature()
print(cpu_temperatures)




import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Введіть дані вашого SMTP сервера
smtp_server = "smtp.gmail.com"
smtp_port = 587
username = "alkost198333@gmai.com"
password = "ваш_пароль"  # Замініть на ваш фактичний пароль

# Налаштування електронного листа
from_email = "alkost198333@gmai.com"
to_email = "адресат@example.com"
subject = "Тема вашого листа"
body = "Це текст вашого електронного листа."

# Створення об'єкту повідомлення
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = subject

# Додавання тексту до повідомлення
msg.attach(MIMEText(body, 'plain'))

# Відправка електронного листа
try:
    # Підключення до SMTP сервера
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)

    # Відправлення листа
    server.send_message(msg)
    print("Лист успішно відправлений!")

except Exception as e:
    print(f"Помилка: {e}")

finally:
    server.quit()