# utils.py
def KelvinToCelsius(temperature_kelvin: float):
    temperature_celsius = temperature_kelvin - 273.15
    return temperature_celsius


def TimeDiffText(seconds: float):
    if seconds <= 0:
        return "0d 0h 0m 0s"
    print("seconds", seconds)
    minutes = seconds // 60
    hours = seconds // 3600
    days = seconds // 86400

    remaining_seconds = seconds % 60
    remaining_minutes = minutes % 60
    remaining_hours = hours % 24

    return f"{int(days)}d {int(remaining_hours)}h {int(remaining_minutes)}m {int(remaining_seconds)}s"
