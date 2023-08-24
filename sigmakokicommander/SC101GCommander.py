from sigmakokicommander.BaseCommander import BaseCommander


# 実装していないコマンドリスト
# MODE:
# MODE?
# C:
# Q:
# !:
# H:
# R:
# Z:
# JG:
# JY:
# I:
# O:
class SC101GCommander(BaseCommander):
    def __init__(self, ser=None):
        super().__init__(ser)
        self.um_per_pulse = 0.1
        self.min_speed = 0  # [um/sec]
        self.max_speed = 2e5  # [um/sec]
        self.min_acceleration_time = 10  # [ms]
        self.max_acceleration_time = 2000  # [ms]

    def reset(self):
        """
        リセット
        :return: True or False
        """
        order = 'RESET:'
        self.send(order)
        return True

    def check_status(self) -> bool:
        """
        現在の状態を取得する
        1,2,3,4,5 の5つの値が返ってくる．
        1: エラー状態の表示 {
            K: 正常
            1: コマンドエラー
            2: スケールエラー
            3: リミット停止
            4: オーバースピードエラー
            5: オーバーフローエラー
            6: エマージェンシーエラー
            7: MN102エラー
            8: リミットエラー
            9:システムエラー
        }
        2: 1軸状態表示 {
            K: 正常停止状態
            M: 正常動作状態
            C: CWリミット停止状態
            W: CCWリミット停止状態
        }
        3: 2軸状態表示 {
            2と同じ
        }
        4: システム予約 {
            メンテナンス用．4桁の数値
        }
        5: ステージ位置決め状態 {
            B: ビジー状態 位置決め未完了状態
            R: レディ状態 位置決め完了状態
        }
        :return: True or False
        """
        order = 'SRQ:'
        self.send(order)
        msg = self.recv()
        # 状態を表示する
        states = msg.split(',')
        if len(states) != 5:
            print('invalid response')
            return False
        # エラー状態
        error_state = states[0]
        if error_state == 'K':
            print('no error')
        elif error_state == '1':
            print('command error')
        elif error_state == '2':
            print('scale error')
        elif error_state == '3':
            print('limit stop')
        elif error_state == '4':
            print('over speed error')
        elif error_state == '5':
            print('overflow error')
        elif error_state == '6':
            print('emergency error')
        elif error_state == '7':
            print('MN102 error')
        elif error_state == '8':
            print('limit error')
        elif error_state == '9':
            print('system error')
        else:
            print('invalid error state')
        # 1軸状態
        axis1_state = states[1]
        if axis1_state == 'K':
            print('axis1: normal stop')
        elif axis1_state == 'M':
            print('axis1: normal moving')
        elif axis1_state == 'C':
            print('axis1: CW limit stop')
        elif axis1_state == 'W':
            print('axis1: CCW limit stop')
        else:
            print('invalid axis1 state')
        # 2軸状態
        axis2_state = states[2]
        if axis2_state == 'K':
            print('axis2: normal stop')
        elif axis2_state == 'M':
            print('axis2: normal moving')
        elif axis2_state == 'C':
            print('axis2: CW limit stop')
        elif axis2_state == 'W':
            print('axis2: CCW limit stop')
        else:
            print('invalid axis2 state')
        # システム予約
        system_reserved = states[3]
        print('system reserved:', system_reserved)
        # ステージ位置決め状態
        position_state = states[4]
        if position_state == 'B':
            print('positioning: busy')
        elif position_state == 'R':
            print('positioning: ready')
        else:
            print('invalid positioning state')
        return True

    def get_position(self) -> bool:
        """
        現在位置を取得する
        self.recv()で値を受け取り，self.um_per_pulseで割るとμm単位での座標値になる．
        :return: True or False
        """
        order = 'P:W'
        self.send(order)
        return True

    def start_moving(self) -> bool:
        """
        駆動開始
        :return:
        """
        order = 'G'
        self.send(order)
        return True

    def move(self, command: str, values: list) -> bool:
        """
        駆動コマンド一般化
        SC101Gはμm単位で指定する．
        :param command:　'A' or 'M'
        :param values:  μm単位の座標値のリスト
        :return: True or False
        """
        if len(values) != 2:
            print('move value list must contain 2 values')
            return False

        x_sign = '+' if values[0] >= 0 else '-'
        y_sign = '+' if values[1] >= 0 else '-'

        order = f'{command}:W{x_sign}P{abs(int(values[0]))}{y_sign}P{abs(int(values[1]))}'
        self.send(order)
        self.start_moving()
        return True

    def move_absolute(self, values: list):
        """
        絶対座標指定駆動
        SC101Gはμm単位で指定する．
        :param values: μm単位の座標値のリスト
        :return:
        """
        self.move('A', values)

    def move_relative(self, values: list) -> bool:
        """
        相対座標指定駆動
        SC101Gはμm単位で指定する．
        :return:
        """
        return self.move('M', values)

    def stop(self, axis) -> bool:
        """
        指定した軸を停止する
        :param axis: 1, 2, 'W' or 'E'
        :return:
        """
        if axis not in [1, 2, 'W', 'E']:
            print('axis must be 1, 2, "W" or "E"')
            return False

        order = f'L:{axis}'
        self.send(order)
        return True

    def set_speed(self, values: list) -> bool:
        """
        速度を設定する
        SC101Gはμm/sec単位で指定する．
        :param values: μm/sec単位の速度のリスト
        :return: True or False
        """
        if len(values) != 2:
            print('speed value list must contain 2 values')
            return False

        for value in values:
            if value < 0 or value > self.max_speed:
                print('speed value must be 0 ~', self.max_speed)
                return False

        order = f'D:WF{int(values[0])}F{int(values[1])}'
        self.send(order)
        return True

    def set_speed_max(self) -> bool:
        """
        最大速度に設定する
        :return: True or False
        """
        return self.set_speed([self.max_speed, self.max_speed])

    def set_acceleration(self, axis: int, value: int) -> bool:
        """
        加速度を設定する
        :param axis: 1 or 2
        :param value: 10 ~ 2000
        :return: True or False
        """
        if value < 10 or value > 2000:
            print('acceleration value must be 10 ~ 2000')
            return False

        order = f'ACC:{axis} {int(value)}'
        self.send(order)
        return True

    def set_acceleration_max(self) -> bool:
        """
        最大加速度に設定する
        :return: True or False
        """
        ret1 = self.set_acceleration(1, self.max_acceleration_time)
        ret2 = self.set_acceleration(2, self.max_acceleration_time)
        return ret1 and ret2
