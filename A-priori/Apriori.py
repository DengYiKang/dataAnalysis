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


def isApriori(Ck_item, Lk_sub_1):
    """
    判断是否满足先验条件，即任何非频繁的(k-1)项集都不是频繁k项集的子集
    :param Ck_item:候选频繁k项集
    :param Lk_sub_1:频繁k-1项集
    :return:true or false
    """
    for item in Ck_item:
        sub_item = Ck_item - frozenset([item])
        if sub_item not in Lk_sub_1:
            return False
    return True


def createCk(Lk_sub_1, k):
    """
    生成候选频繁k项集
    :param Lk_sub_1:频繁k-1项集
    :param k:当前要生成的候选频繁几项集
    :return:候选频繁k项集
    """

    Ck = set()
    len_Lk_sub_1 = len(Lk_sub_1)
    list_Lk_sub_1 = list(Lk_sub_1)
    for i in range(len_Lk_sub_1):  # i: [0, len_Lk_sub_1)
        for j in range(i + 1, len_Lk_sub_1):  # j: [i+1, len_Lk_sub_1)
            l1 = list(list_Lk_sub_1[i])
            l2 = list(list_Lk_sub_1[j])
            l1.sort()
            l2.sort()
            # 判断l1的前k-1-1个元素与l2的前k-1-1个元素对应位是否全部相同
            # 如果相同，那么两者连接生成k项集，若该集满足先验条件，则加入到候选集中
            if l1[0:k - 2] == l2[0:k - 2]:
                Ck_item = list_Lk_sub_1[i] | list_Lk_sub_1[j]
                if isApriori(Ck_item, Lk_sub_1):
                    Ck.add(Ck_item)
    return Ck


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


def generateL(data_set, max_k, min_support):
    """
    生成最高项为k的所有频繁项目集L和对应的support记录support_data
    :param data_set:数据库事务集
    :param max_k:求的最高项目集为k项
    :param min_support:最小支持度
    :return:
    """
    # 创建一个频繁项目集为key，其支持度为value的dict
    support_data = {}
    C1 = createC1(data_set)
    L1 = generateLkByCk(data_set, C1, min_support, support_data)
    Lk_sub_1 = L1.copy()  # 对L1进行浅copy
    L = []
    L.append(Lk_sub_1)  # 末尾添加指定元素
    for k in range(2, max_k + 1):
        Ck = createCk(Lk_sub_1, k)
        Lk = generateLkByCk(data_set, Ck, min_support, support_data)
        Lk_sub_1 = Lk.copy()
        L.append(Lk_sub_1)
    return L, support_data


def generateRule(L, support_data, min_confidence):
    """
    产生关联规则
    :param L:所有的频繁项目集
    :param support_data:项目集-支持度dict
    :param min_confidence:最小置信度
    :return:
    """
    rule_list = []
    sub_set_list = []
    for i in range(len(L)):
        for frequent_set in L[i]:
            for sub_set in sub_set_list:
                if sub_set.issubset(frequent_set):
                    conf = support_data[frequent_set] / support_data[sub_set]
                    # 将rule声明为tuple
                    rule = (sub_set, frequent_set - sub_set, conf)
                    if conf >= min_confidence and rule not in rule_list:
                        rule_list.append(rule)
            sub_set_list.append(frequent_set)
    return rule_list


if __name__ == "__main__":
    data_set = loadDataSet()

    L, support_data = generateL(data_set, 3, 0.2)
    rule_list = generateRule(L, support_data, 0.7)
    for Lk in L:
        print("=" * 55)
        print("frequent " + str(len(list(Lk)[0])) + "-itemsets\t\tsupport")
        print("=" * 55)
        for frequent_set in Lk:
            print(frequent_set, support_data[frequent_set])
    print()
    print("Rules")
    for item in rule_list:
        print(item[0], "=>", item[1], "'s conf: ", item[2])
