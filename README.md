# **pyUnit-NewWord** [![](https://gitee.com/tyoui/logo/raw/master/logo/photolog.png)][1]

## 无监督训练文本词库
[![](https://img.shields.io/badge/Python-3.7-green.svg)](https://pypi.org/project/pyunit-newword/)

## 安装
    pip install pyunit-newword
    
## 注意事项
    该算法采用Hash字典存储，大量消耗内存。100M的纯中文文本需要12G以上的内存，不然耗时太严重。
    
## 训练代码(文本是UTF-8格式)
```python
from pyunit_newword import NewWords

if __name__ == '__main__':
    nw = NewWords(filter_cond=10, filter_free=2)
    nw.add_text(r'C:\Users\Administrator\Desktop\微博数据.txt')
    nw.analysis_data()
    with open('分析结果.txt', 'w', encoding='utf-8')as f:
        for word in nw.get_words():
            print(word)
            f.write(word[0] + '\n')
```

## 爬虫的微博数据一部分截图（大概100M纯文本）
![](./img/weibo.png)
       
## 训练微博数据后的结果
![5个词语](./img/5.png)

### 训练后得到的词语视频
<iframe height=498 width=510 src='http://player.youku.com/embed/XNDUzODYzNzM1Mg==' frameborder=0 'allowfullscreen'></iframe>

***
[1]: https://blog.jtyoui.com
