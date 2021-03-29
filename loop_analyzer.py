import logging
import graphviz as gvz
import json
from constants import crib_path
from logger import logger

class LoopAnalyzer:
    def __init__(self, index, plaintext, ciphertext):
        """
        在密文的某个位置下找到了一个明密文对，起始位置为 index (0 表示文档开头)
        :param index: 明密文对在文档中的起始位置
        :param plaintext: 明文
        :param ciphertext: 密文
        """
        assert len(plaintext) == len(ciphertext)
        self.index = index
        self.plaintext = plaintext.upper()
        self.ciphertext = ciphertext.upper()

    def analyze(self):
        logger.info('Analyzing... Index: %d  Plaintext: %s  Ciphertext: %s' % (self.index, self.plaintext, self.ciphertext))
        G = gvz.Graph()
        for i in range(len(self.plaintext)):
            G.edge(self.plaintext[i], self.ciphertext[i], str(self.index + i))
        G.view()


if __name__ == '__main__':
    with open(crib_path, 'r') as f:
        args = json.load(f)
        analyzer = LoopAnalyzer(args['index'], args['plaintext'], args['ciphertext'])
        analyzer.analyze()
