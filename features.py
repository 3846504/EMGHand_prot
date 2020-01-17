import pandas as pd
import time

def flatten(nested_list):
    """2重のリストをフラットにする関数"""
    return [e for inner_list in nested_list for e in inner_list]

def convert_1d_to_2d(l, cols):
    return [l[i*500:i*500+500:5]+l[i*500+1:i*500+501:5]+l[i*500+2:i*500+502:5]+l[i*500+3:i*500+503:5]+l[i*500+4:i*500+504:5] for i in range(len(l)//500)]

def convert_1d_to_2d2(l, cols):
    return l[0:500:5]+l[1:+501:5]+l[2:502:5]+l[3:503:5]+l[4:504:5]

def features(dataLists):
    maxLists = [sum(data) for data in dataLists]
    maxIndexs = [maxLists[i*200:i*200+200].index(max(maxLists[i*200:i*200+200])) + i*200 for i in range(1, len(maxLists)//200-1)]

    features = [dataLists[i-50:i+50] for i in maxIndexs]
    
    feature = flatten(flatten(features))

    feature = [i/1000 for i in feature]

    features = convert_1d_to_2d(feature, 100)

    return features

def features2(dataLists):
    maxLists = [sum(data) for data in dataLists]
    maxIndex = maxLists.index(max(maxLists))

    features = dataLists[maxIndex-50:maxIndex+50]

    if(len(features) < 100):
        features = dataLists[0:100]
    
    feature = flatten(features)

    feature = [i/1000 for i in feature]

    features = convert_1d_to_2d2(feature, 100)

    return features

if __name__ == "__main__":
    x = int(input("TestNum>>"))
    start = time.time()
    TestData = EMG = pd.read_csv("c:\project\EMG_data\EMG_file_test_2019-12-06.csv")
    data = EMG.iloc[:, x*5:(x*5)+5]
    dataLists = data.values.tolist()

    print(features(dataLists))
    elapsed_time = time.time() - start

    print("elapsed_time:{0}".format(elapsed_time) + "[sec]")