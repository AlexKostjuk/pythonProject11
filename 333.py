import wmi

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

all_sensors = get_all_sensors()
for name, data in all_sensors.items():
    print(f"{name}: {data}")
