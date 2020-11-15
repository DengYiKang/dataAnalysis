import itertools


def loadDataSet():
    data_set = [['e1', 'e2', 'e5'],
                ['e2', 'e4'],
                ['e2', 'e3'],
                ['e1', 'e2', 'e4'],
                ['e1', 'e3'],
                ['e2', 'e3'],
                ['e1', 'e3'],
                ['e1', 'e2', 'e3', 'e5'],
                ['e1', 'e2', 'e3']]
    return data_set


def makeIndex(data_set):
    """
    格式化数据集，将其元素用索引表示，索引从0开始
    :param data_set: 原数据集
    :return: 新数据集，index-data dict
    """
    index_data_set = list()
    data2index = dict()
    index2data = dict()
    for t in data_set:
        tmp_list = list()
        for item in t:
            if item not in data2index:
                cur_index = len(data2index)
                data2index[str(item)] = int(cur_index)
                index2data[int(cur_index)] = str(item)
            tmp_list.append(data2index[str(item)])
        index_data_set.append(tmp_list)
    return index_data_set, index2data


def resumeDataSet(indexed_data_set, index2data):
    """
    将索引化的数据集恢复至原数据集
    :param indexed_data_set: 索引化数据集
    :param index2data: index-data dict()
    :return: data_set
    """
    data_set = list()
    for t in indexed_data_set:
        tmp_list = list()
        for term in t:
            tmp_list.append(index2data[int(term)])
        data_set.append(frozenset(tmp_list))
    return data_set


def getHashCode(a, b, buckets_len):
    return int((a * b) % buckets_len)


def createC1(data_set):
    """
    生成候选频繁1项集
    :param data_set:数据库事务集
    :return:候选频繁1项集
    """

    C1 = set()
    for t in data_set:
        for item in t:
            # 生成不可变set，使得可被其它set加入作为元素
            item_set = frozenset([item])
            # 为生成频繁项目集时扫描数据库时以提供issubset()功能
            C1.add(item_set)
    return C1


def generateC2(data_set, L1, vector, buckets_len):
    """
    生成候选频繁2项集
    :param data_set:数据集
    :param L1:频繁1项集
    :param vector:buckets对应的vector
    :param buckets_len:桶的个数
    :return:候选频繁2项集
    """

    C2 = set()
    for t in data_set:
        for pair in itertools.combinations(t, 2):
            a = frozenset([pair[0]])
            b = frozenset([pair[1]])
            if a not in L1 or b not in L1:
                continue
            hash_code = getHashCode(pair[0], pair[1], buckets_len)
            if vector & (1 << hash_code) == 0:
                continue
            C2.add(frozenset([pair[0], pair[1]]))
    return C2


def generateLkByCk(data_set, Ck, min_support, support_data):
    """
    将不满足支持度的项集删除，由候选频繁k项集生成频繁k项集
    :param data_set: 数据库事务集
    :param Ck: 候选频繁k项集
    :param min_support: 最小支持度
    :param support_data: 项目集-支持度dict
    :return:频繁k项集
    """

    Lk = set()
    # 通过dict记录候选频繁k项集的事务支持个数
    item_count = {}
    for t in data_set:
        for Ck_item in Ck:
            if Ck_item.issubset(t):
                if Ck_item not in item_count:
                    item_count[Ck_item] = 1
                else:
                    item_count[Ck_item] += 1
    data_num = float(len(data_set))
    for item in item_count:
        if (item_count[item] / data_num) >= min_support:
            Lk.add(item)
            support_data[item] = item_count[item] / data_num
    return Lk


def generateVector(data_set, buckets_len, min_support):
    """
    生成vector，第i位上为1表示对应的bucket是frequent的
    :param data_set:索引化后的数据集
    :param buckets_len:桶的数量
    :param min_support:support阈值
    :return:vector (type int)
    """
    buckets = dict()
    vector = int(0)
    # 初始化hashtable
    for i in range(0, buckets_len):
        buckets[i] = 0
    for t in data_set:
        for pair in itertools.combinations(t, 2):
            hash_code = getHashCode(int(pair[0]), int(pair[1]), buckets_len)
            buckets[hash_code] += 1
    data_num = float(len(data_set))
    for index, val in buckets.items():
        if (val / data_num) >= min_support:
            vector |= (1 << index)
    return vector


def firstPass(data_set, buckets_len, min_support):
    """
    first pass，返回频繁1项集L1与vector
    :param data_set:
    :param buckets_len:
    :param min_support:
    :return:L1, vector
    """
    C1 = createC1(data_set)
    support_data = dict()
    # 这里只是把support_data的引用传过去
    L1 = generateLkByCk(data_set, C1, min_support, support_data)
    vector = generateVector(data_set, buckets_len, min_support)
    return L1, vector


def secondPass(data_set, L1, vector, buckets_len, min_support):
    """
    second pass，返回频繁2项集
    :param data_set: 数据集
    :param L1: 频繁1项集
    :param vector: 与buckets对应的vector
    :param buckets_len: buckets个数
    :param min_support: support阈值
    :return:
    """
    C2 = generateC2(data_set, L1, vector, buckets_len)
    support_data = dict()
    L2 = generateLkByCk(data_set, C2, min_support, support_data)
    return L2


def test():
    buckets_len = 4
    min_support = 0.2
    data_set = loadDataSet()
    indexed_data_set, index2data = makeIndex(data_set)
    L1, vector = firstPass(indexed_data_set, buckets_len, min_support)
    L2 = secondPass(indexed_data_set, L1, vector, buckets_len, min_support)
    L2_data = resumeDataSet(list(L2), index2data)
    print(L2_data)


if __name__ == "__main__":
    test()
