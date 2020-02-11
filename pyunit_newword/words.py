#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# @Time  : 2018/2/28 10:58
# @Author: Jtyoui@qq.com
from sklearn.linear_model import LinearRegression
import numpy as np
from tqdm import tqdm
import re
import math
import os


class NewWords:
    def __init__(self, max_split=5, accuracy=0.1, filter_cond=None, filter_free=None):
        """初始化

        当filter_cond=filter_free=None时，会启动预加载模型\n
        0 < accuracy 越小识别的词语越精确，但是生成词语越少

        :param max_split: 最大候选词长度,限制长度为 n-gram
        :param accuracy: 自动寻找候选词和模型的精准度之差，默认是设置：0.1
        :param filter_cond: 过滤凝聚度，默认None为自动寻找
        :param filter_free: 过滤自由度，默认None为自动寻找
        """
        self.vocab = {}
        self.max_split = max_split
        self.accuracy = accuracy
        self.all_words_len = 0
        self.cond = filter_cond
        self.free = filter_free
        self.auto = None
        if not (filter_free and filter_free):
            txt = os.path.dirname(__file__) + os.sep + 'auto.txt'
            d = [data.strip().split('\t') for data in open(txt, 'r', encoding='utf-8').readlines()]
            data = np.array(d, dtype=np.float32)
            x = data[:, :-1]
            y = data[:, -1:]
            self.auto = LinearRegression()
            self.auto.fit(x, y)

    def add_text(self, file, encoding='UTF-8'):
        """读取文本数据内容

        统计：[关键字次数,关键字频率,关键字的左邻,关键字的右邻]

        :param file: 文件文本路径
        :param encoding: 文本格式
        """
        with open(file=file, mode='r', encoding=encoding) as line:
            for word in tqdm(line.readlines(), desc='读取数据进度条'):
                words = word.strip()
                for lines in re.split('[^\u4e00-\u9fa50-9a-zA-Z]', words):
                    match = re.findall(r'[\u4e00-\u9fa50-9]', lines)
                    lens = len(match)
                    self.all_words_len += lens
                    for i in range(lens):
                        for j in range(1, self.max_split + 1):
                            if i + j <= lens:
                                k = ''.join(match[i:i + j])
                                if k in self.vocab:
                                    w = self.vocab[k]
                                else:
                                    w = [0, 0, set(), set()]
                                    self.vocab[k] = w
                                w[0] += 1
                                w[1] = w[0] / self.all_words_len
                                if i != 0:
                                    w[2].add(match[i - 1])
                                if i + j != lens:
                                    w[3].add(match[i + j])
                                else:  # 候选词的个数大于该句子的长度时立即停止
                                    break

    def analysis_data(self):
        """分析文本数据

        分析：关键词每个片段凝固程度：solid\n
             关键字的左邻自由程度：front_all\n
             关键字的右邻自由程度：end_all
        """
        for key in tqdm(self.vocab, desc='分析数据进度条'):
            key_len = len(key)
            if key_len != 1:
                attribute: list = self.vocab[key]
                solid, end_all, front_all = [], 0, 0
                for index in range(1, key_len):
                    score = attribute[1] / (self.vocab[key[:index]][1] * self.vocab[key[index:]][1])
                    solid.append(math.log2(score))
                for front in attribute[2]:
                    front_all -= math.log2(self.vocab[front][1]) * self.vocab[front][1]  # 左邻字集合自由程度
                for end in attribute[3]:
                    end_all -= math.log2(self.vocab[end][1]) * self.vocab[end][1]  # 右邻字集合自由程度
                attribute.append(min(solid))
                attribute.append(min(end_all, front_all))

    def _filter_algorithm(self, x):
        """自动筛选算法

        自动寻找筛选过滤参数值\n
        attribute:[出现次数,出现频率,关键字的左邻,关键字的右邻,凝固程度,自由程度]

        ：:param x: x为候选词属性
        """
        if len(x[0]) == 1:
            return False
        attribute: list = x[1]
        if attribute[4] <= 0.1:
            return False
        elif len(attribute[2]) == len(attribute[3]) == 0 and attribute[0] > 2:
            return True
        elif attribute[0] > 100 and len(attribute[2]) >= attribute[0] * 0.1 and len(attribute[3]) >= attribute[0] * 0.1:
            return True
        if not (self.free and self.cond):
            ls = [attribute[0], attribute[1], len(attribute[2]), len(attribute[3]), attribute[4]]
            predict = self.auto.predict([ls])[0][0]
            if 0 < attribute[5] - predict <= self.accuracy and predict > 0:
                return True
        elif attribute[4] >= self.cond and attribute[5] >= self.free:
            return True
        return False

    def get_words(self):
        """新词筛选"""
        clean_text = filter(self._filter_algorithm, self.vocab.items())
        return clean_text
