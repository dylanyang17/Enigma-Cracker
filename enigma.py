from constants import rotor_notches, default_rotor_circuits, default_plug_board, reflector
import logging

logging.basicConfig(
    format="[%(asctime)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.DEBUG,
)


class Enigma:
    def __init__(self, rotors, ring_setting, position, plug_board):
        """
        :param rotors: tuple，三元组，为 1~5 的数字对应转子类型
        :param ring_setting: str，长度为 3，为转芯与字母环的偏移
        :param position: str，长度为 3，从左到右对应 “从高到低” 三个初始位置
        :param plug_board: str，长度为 26，从左到右对应 A-Z 的插线，要求是一个排列
        """
        assert len(rotors) == 3
        assert type(ring_setting) == str and len(ring_setting) == 3
        assert type(position) == str and len(position) == 3
        assert type(plug_board) == str and len(plug_board) == 26 and ''.join(
            sorted(plug_board.upper())) == default_plug_board

        self.rotors = rotors
        self.ring_setting = ring_setting.upper()
        self.position = position.upper()
        self.plug_board = plug_board.upper()

        self.notches = ''
        self.rotor_circuits = []
        self.rotor_circuits_rev = []
        for i, rotor in enumerate(self.rotors):
            # notches
            self.notches += rotor_notches[rotor]
            # rotor_circuits without ring setting
            tmp_circuit = []
            for j in range(26):
                tmp_circuit.append((self._char_to_index(default_rotor_circuits[rotor][j]) - j) % 26)
            # rotor_circuits_rev without ring setting
            tmp_circuit_rev = [0 for _ in range(26)]
            for p, v in enumerate(tmp_circuit):
                tmp_circuit_rev[(p + v) % 26] = (-v) % 26
            # ring setting
            shift = self._char_to_index(ring_setting[i])
            self.rotor_circuits.append(self._right_shift(tmp_circuit, shift))
            self.rotor_circuits_rev.append(self._right_shift(tmp_circuit_rev, shift))

    def through_plug_board(self, c):
        """
        返回字符 c 通过插线板后的字符
        """
        return self.plug_board[self._char_to_index(c)]

    def through_rotor(self, ind, c, rev):
        """
        返回字符 c 通过从左到右第 ind (0~2)个 rotor 后的字符，rev 表示是否逆向通过
        """
        touch_pos = (self._char_to_index(c) + self._char_to_index(
            self.position[ind])) % 26  # 在当前 position 的情况下字符 c 与转子的接触点下标
        return self._index_to_char(self._char_to_index(c) +
                                   (self.rotor_circuits_rev[ind][touch_pos] if rev else self.rotor_circuits[ind][touch_pos]))

    def through_reflector(self, c):
        """
        返回字符 c 通过 reflector 后的字符
        """
        return reflector[self._char_to_index(c)]

    def through_all(self, c):
        """
        返回字符 c 依次通过插线板->从右到左三个转子->反射器->从左到右三个转子->插线板后的结果
        """
        c = self.through_plug_board(c)
        for i in reversed(range(0, 3)):
            c = self.through_rotor(i, c, False)
        c = self.through_reflector(c)
        for i in range(0, 3):
            c = self.through_rotor(i, c, True)
        return self.through_plug_board(c)

    def rotate(self):
        """
        将转子转动到下一个位置
        """
        rot = self._will_rotate()
        tmp_position = ''
        for i in range(3):
            tmp_position += self._index_to_char((self._char_to_index(self.position[i]) + rot[i]) % 26)
        self.position = tmp_position
        logging.debug('rot: ' + rot.__str__() + '. now: ' + self.position)

    def press(self, c):
        """
        进行按键，转动并返回加密结果
        """
        self.rotate()
        return self.through_all(c)

    def _will_rotate(self):
        """
        返回一个长为 3 的列表，每个位置为 0 或 1 表示是否会旋转
        """
        ret = [0, 0, 1]
        for i in range(1, 3):
            if self.position[i] == self.notches[i]:
                ret[i-1] = 1
                ret[i] = 1
        return ret

    def _right_shift(self, s, c):
        """
        返回字符串 s 循环右移 c 位的结果
        """
        if c < 0:
            return self._left_shift(s, -c)
        return s[len(s) - c:] + s[:len(s) - c]

    def _left_shift(self, s, c):
        """
        返回字符串 s 循环左移 c 位的结果
        """
        if c < 0:
            return self._right_shift(s, -c)
        return s[c:] + s[:c]

    def _char_to_index(self, c):
        """
        将单字符转成下标，例如 A->0，C->2
        """
        assert c.isupper()
        return ord(c) - ord('A')

    def _index_to_char(self, ind):
        """
        将下标按 A-Z 转为字符，例如 0->A，2->C
        """
        return chr(ord('A') + ind % 26)


if __name__ == '__main__':
    enigma = Enigma((1, 2, 3), 'DOE', 'MDV', default_plug_board)
    while True:
        c = input().upper()
        print(enigma.press(c))
