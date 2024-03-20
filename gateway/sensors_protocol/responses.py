import time
from datetime import datetime


def ack_reply(inp): return "@ACK," + str(format(inp, "04")) + "#\r\n"


def rtc_time_reply(): return "@UTC," + str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())) + "#\r\n"


def rtc_time_reply2(inp): return "@UTC," + str(inp) + "#"


def set_rtc():
    print("set RTC time")
    template = "*@CMD,000000,006,"
    now = datetime.utcnow()
    y = now.strftime("%Y")
    m = str(now.strftime("%m"))
    d = str(now.strftime("%d"))
    h = str(now.strftime("%H"))
    mn = str(now.strftime("%M"))
    s = str(now.strftime("%S"))
    out = template + str(y[2:]) + "," + m + "," + d + "," + h + "," + mn + "," + s + "#,#"
    return out


def set_report_time(timer=5):
    if timer < 5 or timer > 1440:
        timer = 5
    return "*@CMD,000000,018," + str(timer) + "#,#\r\n"


def set_tmp(temperature=0, humidity=0):
    print("set calibration for temp/humidity")
    if temperature > 5 or temperature < -5:
        temperature = 0
    if humidity > 10 or humidity < -10:
        humidity = 0
    out = "*@CMD,000000,050,1" + str(temperature) + "," + str(humidity) + "#,#\r\n"
    return out


def clear_flash(): return "*@CMD,*000000,500#,#\r\n"


def reboot(): return "*@CMD,*000000,991#,#\r\n"
