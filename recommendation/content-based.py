# coding: utf-8

# # Assignment 3:  Recommendation systems
#
# Here we'll implement a content-based recommendation algorithm.
# It will use the list of genres for a movie as the content.
# The data come from the MovieLens project: http://grouplens.org/datasets/movielens/

# Please only use these imports.
from collections import Counter, defaultdict
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix


def tokenize_string(my_string):
    """ 正则过滤
    """
    return re.findall('[\w\-]+', my_string.lower())


def tokenize(movies):
    """
    在movies的数据帧中加入新的列'tokens', 'tokens'属性为list, 保存对应电影的类别

    Params:
      movies...电影数据帧
    Returns:
      处理后的电影数据帧

    >>> movies = pd.DataFrame([[123, 'Horror|Romance'], [456, 'Sci-Fi']], columns=['movieId', 'genres'])
    >>> movies = tokenize(movies)
    >>> movies['tokens'].tolist()
    [['horror', 'romance'], ['sci-fi']]
    """
    tokenlist = []
    for index, row in movies.iterrows():
        tokenlist.append(tokenize_string(row.genres))
    movies['tokens'] = tokenlist
    return movies


def featurize(movies):
    """
    在movies数据帧中加入新的列'features', 其属性为(1, num_features)大小的csr_matrix.
    这个矩阵的每一个元素表示对应单词(这里为描述类别的词语)的tf-idf值
    tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i))
    其中i是一个单词(描述类别的词语), d是一个文档(即电影), tf(i, d)为单词i在文档d中出现的次数,
    max_k tf(k, d)为文档d(即电影)中所有种类的单词出现的最大次数
    N是文档(即电影)的总数
    df(i)是包含单词i(描述类别的词语)的文档(即电影)的总数

    Params:
      movies...movies数据帧
    Returns:
      movies, vocab
      movies为处理后的数据帧
      vocab为一个字典，用于将单词映射到从0开始的整数序列
    """

    def tf(word, doc):
        return doc.count(word) / Counter(doc).most_common()[0][1]

    def df(word, doclist):
        return sum(1 for d in doclist if word in d)

    def tfidf(word, doc, dfdict, N):
        return tf(word, doc) * math.log10((N / dfdict[word]))

    def getcsrmatrix(tokens, dfdict, N, vocab):
        matrixRow_list = []
        matrixRow_list = np.zeros((1, len(vocab)), dtype='float')
        for t in tokens:
            if t in vocab:
                matrixRow_list[0][vocab[t]] = tfidf(t, tokens, dfdict, N)
        return csr_matrix(matrixRow_list)

    N = len(movies)
    doclist = movies['tokens'].tolist()
    vocab = {i: x for x, i in enumerate(sorted(list(set(i for s in doclist for i in s))))}

    dfdict = {}
    for v in vocab.items():
        dfdict[v[0]] = df(v[0], doclist)

    csrlist = []
    for index, row in movies.iterrows():
        csrlist.append(getcsrmatrix(row['tokens'], dfdict, N, vocab))

    movies['features'] = csrlist
    return (movies, vocab)


def train_test_split(ratings):
    """
    生成训练集与测试集
    """
    test = set(range(len(ratings))[::1000])
    train = sorted(set(range(len(ratings))) - test)
    test = sorted(test)
    return ratings.iloc[train], ratings.iloc[test]


def cosine_sim(a, b):
    """
    计算余弦相似度, 这里的a, b是对应电影的tf-idf矩阵
    Params:
      a...大小为(1, number_features)的csr_matrix
      b...大小为(1, number_features)的csr_matrix
    Returns:
      余弦相似度 dot(a, b) / ||a|| * ||b||
    """
    v1 = a.toarray()[0]
    v2 = b.toarray()[0]
    return sum(i[0] * i[1] for i in zip(v1, v2)) / (
            math.sqrt(sum([i * i for i in v1])) * math.sqrt(sum([i * i for i in v2])))


def make_predictions(movies, ratings_train, ratings_test):
    """
    预测

    Params:
      movies..........movies数据帧
      ratings_train...训练集
      ratings_test....测试集
    Returns:
      一个numpy数组, 包含对每组测试样例给出的预测评分
    """
    result = []
    # 对测试集中的所有user进行遍历
    for index, row in ratings_test.iterrows():
        # 获取到当前user的所有打过分的电影集mlist
        mlist = list(ratings_train.loc[ratings_train['userId'] == row['userId']]['movieId'])
        # 获取到mlist中所有电影的features矩阵，与mlist中的电影id一一顺序对应
        csrlist = list(movies.loc[movies['movieId'].isin(mlist)]['features'])
        # 获取到当前user的所有打分，其打分与mlist中的电影id一一顺序对应
        mrlist = list(ratings_train.loc[ratings_train['userId'] == row['userId']]['rating'])
        # 获取到所有当前user已打过分的电影与当前测试的电影的余弦相似度
        cmlist = [cosine_sim(c, movies.loc[movies['movieId'] == row['movieId']]['features'].values[0]) for c in csrlist]
        wan = sum([v * mrlist[i] for i, v in enumerate(cmlist) if v > 0])
        wadlist = [i for i in cmlist if i > 0]
        # 如果没有正的余弦相似度，那么用平均值代替
        if (len(wadlist) > 0):
            result.append(wan / sum(wadlist))
        else:
            result.append(np.mean(mrlist))
    return np.array(result)


def mean_absolute_error(predictions, ratings_test):
    """
    计算绝对误差的均值
    """
    return np.abs(predictions - np.array(ratings_test.rating)).mean()


def main():
    path = 'ml-latest-small'
    ratings = pd.read_csv(path + os.path.sep + 'ratings.csv')
    movies = pd.read_csv(path + os.path.sep + 'movies.csv')
    movies = tokenize(movies)
    movies, vocab = featurize(movies)
    print('vocab:')
    print(sorted(vocab.items())[:10])
    ratings_train, ratings_test = train_test_split(ratings)
    print('%d training ratings; %d testing ratings' % (len(ratings_train), len(ratings_test)))
    predictions = make_predictions(movies, ratings_train, ratings_test)
    print('error=%f' % mean_absolute_error(predictions, ratings_test))
    print(predictions)


if __name__ == '__main__':
    main()
