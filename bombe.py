import json
from constants import input_path
from enigma import Enigma


class Bombe:
    def __init__(self, index, ring_setting, initial_position, loops):
        """
        :param
        :param ring_setting: 已知的 ring setting
        :param initial_position: 用于作为猜测起点的初始位置
        :param loops: 列表的列表，注意都是从同一字母出发的环
        """
        self.ring_setting = ring_setting
        self.loops = []
        for loop in loops:
            self.loops.append(self.EnigmaLoop(ring_setting, loop))

    # class EnigmaLoop:
    #     def __init__(self, ring_setting, loop):
    #         self.enigmas = []
    #         for offset in loop:


if __name__ == '__main__':
    with open(input_path, 'r') as f:
        args = json.load(f)
        print(args)
