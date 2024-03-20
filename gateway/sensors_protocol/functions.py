import ipaddress
from datetime import datetime


def hex2bin(h): return bin(int(h, 16))[2:].zfill(len(h) * 4)


def bin2text(s): return "".join([chr(int(s[i:i + 8], 2)) for i in range(0, len(s), 8)])


def bin2hex(str1): return ''.join(hex(int(a, 2))[2:] for a in str1.split())


def to_bcd(inp): return "".join([str(int(inp[i:i + 4], 2)) for i in range(0, len(inp), 4)])


def calculate_voltage(inp): return inp * 10 / 1000


def light_sensor_info(data): return 'bright' if int(data[-1], 2) == 0 else 'dark'


def calculate_mcc(inp): return bin2hex(inp[4:])


def set_ip(p):
    return ipaddress.IPv4Address('%d.%d.%d.%d' % (int(p[0:8], 2), int(p[8:16], 2), int(p[16:24], 2), int(p[24:32], 2)))


def set_rtc(inp):
    y = int(inp[0:8], 2) + 2000
    m = int(inp[8:16], 2)
    d = int(inp[16:24], 2)
    h = int(inp[24:32], 2)
    mm = int(inp[32:40], 2)
    ss = int(inp[40:48], 2)
    date = str(y) + '-' + str(m) + '-' + str(d) + ' ' + str(h) + ':' + str(mm) + ':' + str(ss)
    my_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    return my_date


def type_station(inp):
    if inp == 0:
        st = '2G'
    elif inp == 1:
        st = 'NB'
    elif inp == 16:
        st = 'CATM1'
    else:
        st = 'NULL'
    return st


def type_alarm(inp):
    if inp == 170:  # AA
        st = 'Interval GPRS data'
    elif inp == 10:  # 10
        st = 'Low battery Alarm'
    elif inp == 160:  # A0
        st = 'Temperature/Humidity over threshold'
    elif inp == 161:  # A1:
        st = 'Temperature/Humidity sensor abnormal'
    else:
        st = 'NULL'
    return st


def calculate_mnc(inp):
    if int(bin2hex(inp[0:4]), 2) == 0:
        out = bin2hex(inp[8:])
    else:
        out = bin2hex(inp[4:])
    return out


def calculate_cqr(a):
    if a <= 9:
        return 'Marginal'
    elif a <= 14:
        return 'OK'
    elif a <= 19:
        return 'Good'
    else:
        return 'Excellent'


def calculate_temperature(inp):
    if int(inp[0:1], 2) == 1:
        return -1
    else:
        k = 1 if int(inp[1:2], 2) == 0 else -1
        return int(inp[2:16], 2) * k * 0.1


def calculate_humidity(inp):
    if int(inp[0:1], 2) == 1:
        return -1
    else:
        return int(inp[1:16], 2)/10


def signal_lbs_info(data):
    # base_station_type = type_station(int(data[0:2], 2))
    # signal_lbs_information_length = int(data[4:8], 2)
    mcc = calculate_mcc(data[8:24])
    mnc = calculate_mnc(data[24:40])
    lac = int(data[40:56], 2)
    cell_id = int(data[56:88], 2)
    # return {'Signal_LBS_information_length': signal_lbs_information_length,
    #        'base_station_type': base_station_type,
    #        'MCC': str(mcc),
    #        'MNC': str(mnc),
    #        'LAC': str(lac),
    #        'CELL_ID': cell_id,
    #        }
    return {
        'mcc': str(mcc),
        'mnc': str(mnc),
        'lac': str(lac),
        'cid': cell_id,
    }


def terminal_info(data):
    # btn_1 = int(data[2:3], 2)  # not used since it's not relevant
    # btn = int(data[3:4], 2)  # not used since 5th bit not used
    mode = 'Normal work mode' if int(data[0:2], 2) == 0 else 'Flight mode'
    sensor = 'sensor is normal' if int(data[4:5], 2) == 0 else 'sensor is abnormal'
    sensor_2 = 'sensor is normal' if int(data[5:6], 2) == 0 else 'sensor is over threshold'
    battery_v = 'battery low voltage' if int(data[6:7], 2) == 1 else 'battery is normal'
    machine_c = 'machine is charging' if int(data[7:8], 2) == 1 else 'machine is not charging'
    out = {'work mode': mode,
           'sensor': sensor,
           'sensor_2': sensor_2,
           'battery_v': battery_v,
           'machine_c': machine_c
           }
    return out


def gsm_status(data):
    # btn_1 = int(data[1:2], 2)  # not used since it's not relevant
    conn = 'Internet connection not established' if int(data[2:3], 2) == 0 else 'Internet connection is established'
    gprs = 'GPRS is not registered' if int(data[3:4], 2) == 0 else 'GPRS is registered successful'
    gms_mode = 'GSM is in home network mode' if int(data[4:5], 2) == 0 else 'GSM is in roaming mode'
    gms_registered = ' GSM is not registered yet' if int(data[5:6], 2) == 0 else 'GSM is registered successfully'
    sim_card = 'Not detected SIM card' if int(data[6:7], 2) == 0 else 'Detected SIM card'
    gms_module = 'The GSM module is not started yet' if int(data[7:8], 2) == 0 else 'The GSM module is started'
    out = {'connection': conn,
           'GPRS': gprs,
           'GSM_mode': gms_mode,
           'GSM_registered': gms_registered,
           'SIM_card': sim_card,
           'GSM_module': gms_module
           }
    return out


