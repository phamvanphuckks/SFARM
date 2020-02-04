import minimalmodbus
import serial
import serial.tools.list_ports
import constant as CONSTANT


class Gateway():
    # init MOSBUS RTU
    def __init__(self, port_name, id_device=1):
        self.instrument = minimalmodbus.Instrument(port_name, id_device)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.timeout = 0.05
        self.instrument.mode = minimalmodbus.MODE_RTU  # seconds
    # convert data to int 16

    def convert_data(self, data):
        value = ''
        for i in range(0, len(data)):
            value += hex(data[i])
        value = value.replace('0x', '')
        value = '0x'+value
        return int(value, 16)
    # get number of node of Wriless

    def get_num_of_node(self):
        data = self.instrument.read_registers(
            registeraddress=272, number_of_registers=2, functioncode=3)
        value = self.convert_data(data)
        return value
    # get id of node
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_node_id(self, option):
        value = ''
        if (option == 1):
            data = self.instrument.read_registers(
                registeraddress=273, number_of_registers=2, functioncode=3)
            value = self.convert_data(data)
            return str(value)
        elif (option == 2):
            data = self.instrument.read_registers(
                registeraddress=275, number_of_registers=2, functioncode=3)
            value = self.convert_data(data)
            return str(value)
        elif (option == 3):
            data = self.instrument.read_registers(
                registeraddress=277, number_of_registers=2, functioncode=3)
            value = self.convert_data(data)
            return str(value)
        else:
            print("Khong co device nay!")
            return - 1
    # read mosbus adr

    def get_modbus_adr(self):
        data = self.instrument.read_registers(
            registeraddress=256, number_of_registers=1, functioncode=3)
        value = self.convert_data(data)
        return value
    # read mosbus baudrate

    def get_modbus_baudrate(self):
        data = self.instrument.read_registers(
            registeraddress=257, number_of_registers=1, functioncode=3)
        value = self.convert_data(data)
        return value
    # read mosbus parity

    def get_modbus_parity(self):
        data = self.instrument.read_registers(
            registeraddress=258, number_of_registers=1, functioncode=3)
        value = self.convert_data(data)
        return value
    # get main parmeter
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_main_parameter(self, option=1):
        if (option == 1):
            data = self.instrument.read_float(
                registeraddress=41217, number_of_registers=2, functioncode=3)
            return round(data, 2)
        elif (option == 2):
            data = self.instrument.read_registers(
                registeraddress=41473, number_of_registers=1, functioncode=3)
            return round((data[0]/10), 2)
        elif (option == 3):
            data = self.instrument.read_float(
                registeraddress=41729, number_of_registers=2, functioncode=3)
            return round(data, 2)
    # get temperater of
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_second_parameter(self, option=1):
        if (option == 1):
            data = self.instrument.read_float(
                registeraddress=41220, number_of_registers=2, functioncode=3)
            return round(data, 2)
        elif (option == 2):
            data = self.instrument.read_float(
                registeraddress=41476, number_of_registers=2, functioncode=3)
            return round(data, 2)
        elif (option == 3):
            data = self.instrument.read_float(
                registeraddress=41732, number_of_registers=2, functioncode=3)
            return round(data, 2)
    # get Batterry
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_battery(self, option=1):
        if (option == 1):
            data = self.instrument.read_register(
                41216)
        elif (option == 2):
            data = self.instrument.read_register(
                41472)
        elif (option == 3):
            data = self.instrument.read_register(
                41728)
        return data
    # get Status Node
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_status_node(self, option=1):
        if (option == 1):
            data = self.instrument.read_register(
                41219)
        elif (option == 2):
            data = self.instrument.read_register(
                41475)
        elif (option == 3):
            data = self.instrument.read_register(
                41731)
        return CONSTANT.STATUS_NODE[str(data)]
    # get RF signal
    ''' option:
        1: RELAY
        2: SOIL MOISTURE
        3: HUMIDITY
    '''

    def get_RFsignal(self, option=1):
        data = self.instrument.read_registers(
            registeraddress=68, number_of_registers=1, functioncode=3)
        data = hex(data[0]).replace('0x', '')
        hi_byte = data[0]
        lo_byte = data[len(data) - 1]
        if (option % 2 != 0):
            if (option == 1):
                return CONSTANT.RSSI[str(hi_byte)]
            else:
                data = self.instrument.read_registers(
                    registeraddress=69, number_of_registers=1, functioncode=3)
                data = hex(data[0]).replace('0x', '')
                hi_byte = data[0]
                lo_byte = data[len(data) - 1]
                return CONSTANT.RSSI[str(hi_byte)]
        else:
            return CONSTANT.RSSI[str(lo_byte)]
    # have 2 relay
    # option: 1 or 2
    # 1 is on 0 is off

    def control_RL(self, option, status):
        if (option == 1):
            self.instrument.write_register(registeraddress=2000, value=status,
                                           number_of_decimals=0, functioncode=16, signed=False)
        else:
            self.instrument.write_register(registeraddress=2001, value=status,
                                           number_of_decimals=0, functioncode=16, signed=False)
    # get status of relay

    def get_status_RL(self, option):
        if (option == 1):
            data = self.instrument.read_registers(
                registeraddress=2000, number_of_registers=1, functioncode=3)
        else:
            data = self.instrument.read_registers(
                registeraddress=2001, number_of_registers=1, functioncode=3)
        return data[0]
