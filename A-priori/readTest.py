import csv


def readFile(file):
    with open('Groceries.csv', 'r') as f:
        reader = csv.reader(f)
        result = list(reader)
        data_set = list()
        for term in result:
            str = term[1]
            tmp_list = str[1:-1].split(',')
            data_set.append(tmp_list)
        return data_set


if __name__ == "__main__":
    data = readFile('Groceries.csv')
    for term in data:
        print(term)
