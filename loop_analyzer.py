import logging
import graphviz as gvz
import json
from constants import input_path
from logger import logger


class LoopAnalyzer:
    def __init__(self, plaintext, ciphertext):
        """
        在密文的某个位置下找到了一个明密文对，进行图的绘制以便分析 loop，输出时起始下标为 0
        :param plaintext: 明文
        :param ciphertext: 密文
        """
        assert len(plaintext) == len(ciphertext)
        self.plaintext = plaintext.upper()
        self.ciphertext = ciphertext.upper()

    def analyze(self):
        logger.info('Analyzing... Plaintext: %s  Ciphertext: %s' % (self.plaintext, self.ciphertext))
        G = gvz.Graph()
        for i in range(len(self.plaintext)):
            G.edge(self.plaintext[i], self.ciphertext[i], str(i))
        G.view()


if __name__ == '__main__':
    with open(input_path, 'r') as f:
        args = json.load(f)
        analyzer = LoopAnalyzer(args['plaintext'], args['ciphertext'])
        analyzer.analyze()
