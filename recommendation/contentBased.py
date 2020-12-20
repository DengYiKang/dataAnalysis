from collections import Counter
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix
from recommendation import minihash


def tokenize_string(my_string):
    """
    正则过滤, 返回my_string中所有的合法单词, 同时小写化, 类似split
    :param my_string:
    :return:
    """

    return re.findall('[\w\-]+', my_string.lower())


def tokenize(movies):
    """
    在movies的数据帧中加入新的列'tokens', 'tokens'属性为list, 保存对应电影的类别
    :param movies:电影数据帧
    :return:处理后的电影数据帧
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

    :param movies:movies数据帧
    :return:
    (movies, vocab)
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


def make_predictions(movies, ratings_train, ratings_test, sim_matrix, movies_map):
    """
    预测
    :param movies: movies数据帧
    :param ratings_train: 测试集
    :param ratings_test: 训练集
    :param sim_matrix:相似度矩阵
    :param movies_map:moviesId-index的映射表
    :return:一个numpy数组, 包含对每组测试样例给出的预测评分
    """
    result = []
    # 对测试集中的所有user进行遍历
    for index, row in ratings_test.iterrows():
        # 获取到当前user的所有打过分的电影集mlist
        mlist = list(ratings_train.loc[ratings_train['userId'] == row['userId']]['movieId'])
        # 获取到当前user的所有打分，其打分与mlist中的电影id一一顺序对应
        mrlist = list(ratings_train.loc[ratings_train['userId'] == row['userId']]['rating'])
        # 获取到所有当前user已打过分的电影与当前测试的电影的余弦相似度
        cmlist = [sim_matrix[movies_map[row['movieId']]][movies_map[otherId]] for otherId in mlist]
        wan = sum([v * mrlist[i] for i, v in enumerate(cmlist) if v > 0])
        wadlist = [i for i in cmlist if i > 0]
        # 如果没有正的余弦相似度，那么用平均值代替
        if (len(wadlist) > 0):
            result.append(wan / sum(wadlist))
        else:
            result.append(np.mean(mrlist))
    return np.array(result)


def sse(predictions, ratings_test):
    """
    计算SSE
    """
    return np.abs(np.power(predictions - np.array(ratings_test.rating), 2)).sum()


def get_feature_matrix1(movies, vocab):
    """
    得到n*m的01特征矩阵,n为movies的数量，m为feature的数量
    :param movies: movies数据帧
    :param vocab:类型映射表
    :return:一个n*m的numpy数组
    """
    feature_list = []
    for index, row in movies.iterrows():
        current_list = [0 for _ in range(len(vocab))]
        for t in row['tokens']:
            if t in vocab:
                current_list[vocab[t]] = 1
        feature_list.append(current_list)
    feature_matrix = np.asarray(feature_list)
    return feature_matrix


def get_feature_matrix2(movies, vocab):
    """
    得到n*m的tf-idf特征矩阵,n为movies的数量,m为feature的数量
    :param movies: movies数据帧
    :param vocab:类型映射表
    :return:一个n*m的numpy数组
    """
    feature_matrix = np.zeros((len(movies), len(vocab)))
    for index, row in movies.iterrows():
        feature = row['features'].toarray()[0]
        feature_matrix[index] = feature
    return feature_matrix


def get_cosine_sim(feature_matrix):
    """
    得到m*m的相似度矩阵,m为movies的数量
    :param feature_matrix: 特征矩阵
    :return: numpy的m*m的数组
    """
    similarity = np.dot(feature_matrix, feature_matrix.T)
    square_mag = np.diag(similarity)
    inv_square_mag = 1 / square_mag
    inv_square_mag[np.isinf(inv_square_mag)] = 0
    inv_mag = np.sqrt(inv_square_mag)
    cosine = similarity * inv_mag
    cosine = cosine.T * inv_mag
    return cosine


def main():
    path = 'ml-latest-small'
    # ratings = pd.read_csv(path + os.path.sep + 'ratings.csv')
    movies = pd.read_csv(path + os.path.sep + 'movies.csv')
    movies = tokenize(movies)
    movies, vocab = featurize(movies)
    movies_map = {row['movieId']: index for index, row in movies.iterrows()}
    # cosSim+tf-idf
    # sim_matrix = get_cosine_sim(get_feature_matrix2(movies, vocab))
    # miniHash
    sim_matrix = minihash.miniHash(get_feature_matrix1(movies, vocab).T)
    print('vocab:')
    print(sorted(vocab.items())[:10])
    ratings_train = pd.read_csv(path + os.path.sep + 'train_set.csv')
    ratings_test = pd.read_csv(path + os.path.sep + 'test_set.csv')
    # ratings_train, ratings_test = train_test_split(ratings)
    print('%d training ratings; %d testing ratings' % (len(ratings_train), len(ratings_test)))
    predictions = make_predictions(movies, ratings_train, ratings_test, sim_matrix, movies_map)
    print('SSE=%f' % sse(predictions, ratings_test))
    print(predictions)


if __name__ == '__main__':
    main()
