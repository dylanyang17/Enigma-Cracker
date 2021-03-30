import json
import time
import itertools
from collections import deque

from constants import input_path, output_path
from enigma import Enigma
from constants import default_plug_board
from logger import logger


class Bombe:
    def __init__(self, rotors, ring_setting, offset, plaintext, ciphertext, central_letter, initial_position='AAA'):
        """
        **一定注意在按下时，是先转动后加密，所以这里所有的 enigma 机都是多转动一格后的样子，guess_position 存储 base_engima 转动前的位置**
        :param rotors: list，长度为 3 的列表，取值为 1~5，表示外部枚举的转子类型列表
        :param ring_setting: str，长度为 3，已知的 ring setting
        :param offset: int，明密文对在文档中的偏移
        :param plaintext: str，明文
        :param ciphertext: str，密文
        :param central_letter: str，长度为 1，经过环分析后选择的所在环最多的字符
        :param initial_position: str，长度为 3，用于作为猜测初始位置的起点，一般可随意设定，**需要**
        """
        assert len(rotors) == 3
        assert type(ring_setting) == str and len(ring_setting) == 3
        assert len(plaintext) == len(ciphertext)
        assert type(central_letter) == str and len(central_letter) == 1
        assert type(initial_position) == str and len(initial_position) == 3

        self.rotors = rotors
        self.offset = offset
        self.texts = [plaintext, ciphertext]
        self.central_letter = central_letter.upper()
        self.ring_setting = ring_setting
        self.initial_position = initial_position
        self.guess_position = initial_position
        self.base_enigma = Enigma(rotors, ring_setting, initial_position, default_plug_board)
        self.base_enigma.rotate()
        self.enigmas = []
        tmp_enigma = Enigma(rotors, ring_setting, initial_position, default_plug_board)
        tmp_enigma.rotate()
        for i in range(offset):
            tmp_enigma.rotate()
        for i in range(len(plaintext)):
            self.enigmas.append(Enigma(rotors, ring_setting, tmp_enigma.position, default_plug_board))
            tmp_enigma.rotate()

    def rotate(self):
        self.guess_position = self.base_enigma.position
        self.base_enigma.rotate()
        for enigma in self.enigmas:
            enigma.rotate()

    def check(self, checking_letter):
        """
        BFS 检验中心字符经过插线板后能否变为 c，也就是检验了映射唯一性和 loop，检验成功则返回 Ture 和推导出的映射关系，否则返回 False 和 None
        """
        plug_board = {self.central_letter: checking_letter, checking_letter: self.central_letter}
        indexes = {}  # 用于存储每个字母出现的位置，加速搜索，每一项形如 'T': [(0/1, pos)] 表示在明/密文中的 pos 位置出现
        for i in range(2):  # 枚举是明文还是密文
            for pos in range(len(self.texts[i])):  # 枚举明密文内容
                c = self.texts[i][pos]
                tmp_indexes = indexes.get(c, [])
                tmp_indexes.append((i, pos))
                indexes[c] = tmp_indexes

        visit = {self.central_letter: True, checking_letter: True}
        queue = deque()
        queue.append(self.central_letter)
        if checking_letter != self.central_letter:
            queue.append(checking_letter)
        while len(queue) > 0:
            a = queue.popleft()
            tmp_indexes = indexes.get(a, [])
            for (i, pos) in tmp_indexes:
                x = plug_board[a]
                y = self.enigmas[pos].through_all(x)
                b = self.texts[i ^ 1][pos]
                if (plug_board.get(y) is not None and plug_board[y] != b) \
                        or (plug_board.get(b) is not None and plug_board[b] != y):
                    return False, None
                plug_board[y] = b
                plug_board[b] = y
                if not visit.get(b, False):
                    visit[b] = True
                    queue.append(b)
                if not visit.get(y, False):
                    visit[y] = True
                    queue.append(y)
        return True, plug_board

    def run(self):
        logger.debug(f'Bombe running... rotors: {self.rotors}, ring_setting: {self.ring_setting}')
        settings = []
        start_time = time.time()
        while True:
            for i in range(ord('A'), ord('Z') + 1):
                c = chr(i)
                flag, plug_board = self.check(c)
                if flag:
                    setting = {
                        'rotors': self.rotors,
                        'ring_setting': self.ring_setting,
                        'position': self.guess_position,
                        'plug_board': plug_board
                    }
                    settings.append(setting)
                    logger.info(setting)
            self.rotate()
            if self.guess_position == self.initial_position:
                break
        logger.debug(f'All positions are enumerated. time consumption: {time.time()-start_time}, rotors: {self.rotors}, ring_setting: {self.ring_setting}')
        return settings


class Cracker:
    def run(self, ring_setting, offset, plaintext, ciphertext, central_letter):
        settings = []
        for rotors in itertools.permutations([1, 2, 3, 4, 5], 3):
            bombe = Bombe(list(rotors), ring_setting, offset, plaintext, ciphertext, central_letter)
            settings.extend(bombe.run())
        return settings


if __name__ == '__main__':
    with open(input_path, 'r') as f:
        args = json.load(f)
        cracker = Cracker()
        settings = cracker.run(args['ring_setting'], args['offset'], args['plaintext'], args['ciphertext'], args['central_letter'])
        logger.info(f'Cracker finished. Output: {settings}')
        with open(output_path, 'w') as fw:
            json.dump(settings, fw)
