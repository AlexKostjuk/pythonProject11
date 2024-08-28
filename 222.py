import wmi
import socket

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

all_sensors = get_all_sensors()
computer_name = get_computer_name()

data = {
    "ComputerName": computer_name,
    "Sensors": all_sensors
}

print(all_sensors)
