#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# @Time  : 2018/2/28 10:58
# @Author: Jtyoui@qq.com
import re
import math


class NewWords:
    def __init__(self, max_split=5, filter_cond=None, filter_free=None):
        """初始化

        字母 n 表示 max_split
        词频>200, 凝固度>10^{(n-1)}，自由度>1.5；\n
        词频>30, 凝固度>20^{(n-1)}，自由度>1.0;

        :param max_split: 最大候选词长度,限制长度为 n-gram
        :param filter_cond: 过滤凝聚度，默认None为自动寻找
        :param filter_free: 过滤自由度，默认None为自动寻找
        """
        self.vocab = {}
        self.max_split = max_split
        self.all_words_len = 0

    def add_text(self, file, encoding='UTF-8'):
        """读取文本数据内容

        [出现次数,出现频率,关键字的左邻,关键字的右邻]

        :param file: 文件文本路径
        :param encoding: 文本格式
        """
        with open(file=file, mode='r', encoding=encoding) as line:
            for word in line:
                words = word.strip()
                for lines in re.split('[，,。.！!?？：:]', words):
                    match = re.findall(r'[\u4e00-\u9fa5]', lines)
                    words = ''.join(match)
                    lens = len(words)
                    self.all_words_len += lens
                    for i in range(lens):
                        for j in range(1, self.max_split + 1):
                            if i + j <= lens:
                                k = words[i:i + j]
                                w = self.vocab.get(k)
                                if w:
                                    w[0] += 1
                                    w[1] = w[0] / self.all_words_len
                                    if i != 0:
                                        w[2].append(words[i - 1])
                                    if i + j != lens:
                                        w[3].append(words[i + j])
                                else:
                                    if i == 0:
                                        if len(k) == lens:
                                            self.vocab[k] = [1, 1 / self.all_words_len, [], []]
                                        else:
                                            self.vocab[k] = [1, 1 / self.all_words_len, [], [words[i + j]]]
                                    elif i + j == lens:
                                        if len(k) == lens:
                                            self.vocab[k] = [1, 1 / self.all_words_len, [], []]
                                        else:
                                            self.vocab[k] = [1, 1 / self.all_words_len, [words[i - 1]], []]
                                    else:
                                        self.vocab[k] = [1, 1 / self.all_words_len, [words[i - 1]], [words[i + j]]]

    def analysis_data(self):
        """分析文本数据

        [出现次数,出现频率,关键字的左邻,关键字的右邻,凝固程度,自由程度]
        """
        for key in self.vocab:
            key_len = len(key)
            if key_len != 1:
                attribute: list = self.vocab[key]
                solid, end_all, front_all = [], 0, 0
                for index in range(1, key_len):
                    score = attribute[1] / (self.vocab[key[:index]][1] * self.vocab[key[index:]][1])
                    solid.append(score)
                for front in attribute[2]:
                    front_all -= math.log2(self.vocab[front][1]) * self.vocab[front][1]  # 左邻字集合自由程度
                for end in attribute[3]:
                    end_all -= math.log2(self.vocab[end][1]) * self.vocab[end][1]  # 右邻字集合自由程度
                attribute.append(sum(solid) / len(solid))
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
        if attribute[0] > 50 and attribute[-2] > 100 and attribute[-1] > 2:
            return True
        return False

    def get_words(self):
        """新词筛选"""
        clean_text = filter(self._filter_algorithm, self.vocab.items())
        return sorted(dict(clean_text).items(), key=lambda x: x[1][0], reverse=True)
