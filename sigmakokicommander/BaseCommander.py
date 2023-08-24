import serial


class BaseCommander:
    def __init__(self, ser=None):
        self.ser: serial.Serial = ser
        self.end = '\r\n'

        self.encoding = None

    def send(self, order: str):
        if self.ser is None:
            return
        order += self.end
        self.ser.write(order.encode(self.encoding))

    def recv(self) -> str:
        if self.ser is None:
            return 'some response'
        msg = self.ser.readline().decode()
        msg.strip(self.end)
        return msg
