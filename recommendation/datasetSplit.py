import pandas as pd
import os


def main():
    path = 'ml-latest-small'
    ratings = pd.read_csv(path + os.path.sep + 'ratings.csv')
    u_list = ratings['userId'].tolist()
    u_firstline = {}
    for index, term in enumerate(u_list):
        if term not in u_firstline:
            u_firstline[term] = index
    u_set = set(u_list)
    u_dict = {item: u_list.count(item) for item in u_set}
    sorted_u = sorted(u_dict.items(), key=lambda x: x[1], reverse=True)
    print(sorted_u)
    test = []
    for _ in range(100):
        test.append(u_firstline[sorted_u[_][0]])
    print(test)
    train = sorted(set(range(len(ratings))) - set(test))
    test_df = ratings.iloc[test]
    train_df = ratings.iloc[train]
    test_df.to_csv(path + os.path.sep + 'test_set.csv', index=False)
    train_df.to_csv(path + os.path.sep + 'train_set.csv', index=False)


if __name__ == '__main__':
    main()
