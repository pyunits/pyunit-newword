#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
# @Time  : 2018/2/28 10:58
# @Author: Jtyoui@qq.com
from pyunit_newword import NewWords


def test():
    """测试"""
    nw = NewWords(filter_cond=10, filter_free=2)
    nw.add_text(r'C:\Users\Administrator\Desktop\西游记1.txt')
    nw.analysis_data()
    with open('分析结果.txt', 'w', encoding='utf-8')as f:
        for word in sorted(tuple(nw.get_words()), key=lambda x: len(x[0]), reverse=True):
            print(word)
            f.write(word[0] + '\n')


if __name__ == '__main__':
    test()
