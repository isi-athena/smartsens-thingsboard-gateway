from .functions import *


def convert_input(data):
    data = data.hex()
    if len(data) > 4:
        if data[0:4] == "545a":
            data = hex2bin(data)
            valid = 1
            if bin2text(data[32:48]) == '$D':
                valid = 2
        else:
            valid = -1
    else:
        valid = -1
    return data, valid


def parse_input(data):
    output = {}
    temp = data
    output, second = header(temp, output)
    output, second = time_rtc(second, output)
    output, second = lbs(second, output)
    output, second = status(second, output)
    output = packet_info(second, output)
    return output


def header(data, out):
    hardware_type = data[48:64]
    type_h = "TT18" if int(bin2hex(hardware_type), 16) == 0x0407 else "NULL"
    # out["start_bits"] = bin2text(data[0:16])
    out["packet_length"] = int(data[16:32], 2)
    # out["protocol_number"] = bin2text(data[32:48])
    # out["hardware_type"] = type_h
    out["firmware_version"] = str(set_ip(data[64:96]))
    # out["IMEI"] = to_bcd(data[96:160])
    out["IMEI"] = bin2hex(data[96:160])
    return out, data[160:]


def time_rtc(data, out):
    out['RTC_time'] = str(set_rtc(data[0:48]))
    return out, data[48:]


def lbs(data, out):
    out["LBS_data_length"] = int(data[16:32], 2)
    out["number_of_LBS"] = int(data[32:40], 2)
    # out['LSB_base_stations'] = []
    out['cells'] = []
    if out["number_of_LBS"] > 0:
        eng_pa = (int(data[16:32], 2) - 1) * 8 / (int(data[32:40], 2))
        for i in range(0, int(data[32:40], 2)):
            temp = data[40 + i * int(eng_pa):40 + (i + 1) * int(eng_pa)]
            signal_lsb_information = signal_lbs_info(temp)
            # out['LSB_base_stations'].append(signal_lsb_information)
            out['cells'].append(signal_lsb_information)
        # print(32+int(data[16:32], 2)*8)
    return out, data[32 + int(data[16:32], 2) * 8:]


def status(data, out):
    out["Status_length"] = int(data[0:16], 2)
    out["alarm_type"] = type_alarm(int(data[16:24], 2))
    # out["Terminal_information"] = terminal_info(data[24:32])
    out["mode"] = "Normal work mode" if int(data[24:26], 2) == 0 else "Flight mode"
    out["sensor_info"] = "sensor is normal" if int(data[26:27], 2) == 0 else "sensor is abnormal"
    out["sensor_info_2"] = "sensor is normal" if int(data[27:28], 2) == 0 else "sensor is over threshold"
    out["battery_v"] = "battery low voltage" if int(data[28:29], 2) == 1 else "battery is normal"
    out["charging"] = "machine is charging" if int(data[30:31], 2) == 1 else "machine is not charging"
    out["GMS_signal_strength"] = calculate_cqr(int(data[32:40], 2))
    out["conn"] = "connection not established" if int(data[42:43], 2) == 0 else "connection established"
    out["gprs"] = "GPRS not registered" if int(data[43:44], 2) == 0 else "GPRS registered"
    out["gms_mode"] = "GSM is in home network mode" if int(data[44:45], 2) == 0 else "GSM is in roaming mode"
    out["gms_registered"] = "GSM is not registered" if int(data[45:46], 2) == 0 else "GSM is registered successfully"
    out["sim_card"] = "Not detected SIM card" if int(data[46:47], 2) == 0 else "Detected SIM card"
    out["gms_module"] = "The GSM module is not started yet" if int(data[47:48], 2) == 0 else "The GSM module is started"
    # out["GMS_status"] = gsm_status(data[40:48])
    out["battery_v"] = calculate_voltage(int(data[48:64], 2))
    out["temperature"] = calculate_temperature(data[64:80])
    out["humidity"] = calculate_humidity(data[80:96])
    out["Light_Sensor"] = light_sensor_info(data[96:104])
    return out, data[104:]


def packet_info(data, out):
    out["Packet_index"] = int(data[0:16], 2)
    out["CRC"] = int(data[16:32], 2)
    # out["Stop bits"] = int(data[32:48], 2)
    return out
