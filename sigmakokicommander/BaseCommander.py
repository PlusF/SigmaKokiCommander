import serial


class BaseCommander:
    def __init__(self, ser=None):
        self.ser: serial.Serial = ser
        self.end = '\r\n'

        self.um_per_pulse = 0.01
        self.max_speed = 4000000 * self.um_per_pulse  # [um]

    def send(self, order: str):
        if self.ser is None:
            return
        order += self.end
        self.ser.write(order.encode())

    def recv(self) -> str:
        if self.ser is None:
            return 'some response'
        msg = self.ser.readline().decode()
        msg.strip(self.end)
        return msg
