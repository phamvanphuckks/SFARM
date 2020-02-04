#Serial
import serial
import serial.tools.list_ports

# file này giao tiếp với GateWay(Đỏ) : 


class Gateway1():
    def __init__(self, port_name, baudrate, timeout): #khởi tạo serial
        self.ser = serial.Serial()
        self.ser.port = str(port_name)
        self.ser.baudrate = baudrate
        self.ser.timeout = timeout

    def open(self): # mở cổng COM
        if (self.ser.is_open == False):
            self.ser.open()

    def write_data(self, data): # ghi dữ liệu từ máy tính xuống GateWay(Đỏ)
        self.ser.write(data.encode('utf-8'))

    def read_data(self): # đọc tất cả các dòng
        return self.ser.readlines()


def load_data(): # load data 
    data = GW.read_data()
    if (len(data) != 0):
        for i in range(0, len(data)):
            data[i] = data[i].decode('utf-8')
        Str = data[0]
        Str1 = data[1]
        now = datetime.now()
        timestamp = int(datetime.timestamp(now))
        now = datetime.fromtimestamp(timestamp)
        payload = {
            'LEN': Str[Str.find('LEN:') + len("LEN:"):Str.find(',', Str.find('LEN:') + len("LEN:"))],
            'RSSI': Str[Str.find('RSSI:') + len("RSSI:"):Str.find(',', Str.find('RSSI:') + len("RSSI:"))],
            'SNR': Str[Str.find("SNR:") + len("SNR:"):len(Str) - 2],
            'DATA': bytes.fromhex(Str1[Str1.find("\"") +
                                       1: Str1.find("\"", 1 + int(Str1.find("\"")))]).decode('utf-8'),
            'TIME': now}
        print(payload)
