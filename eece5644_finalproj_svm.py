import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
import math
from sklearn.metrics import classification_report, confusion_matrix


# find score of a classifier
# compares predicted traffic volume to real traffic volume, if within 5% of real, it is deemed correct
def get_score(sv_classifier, xtest, ytest, error):
    y_pred = sv_classifier.predict(xtest)
    count = 0
    for i in range(0, len(y_pred)):
        delta = ytest.iloc[i] * error
        if ytest.iloc[i] - delta < y_pred[i] < ytest.iloc[i] + delta:
            count = count + 1

    return count / len(y_pred)


input_data = pd.read_csv("CleanedData_new.csv")
# Preview the first 5 lines of the loaded data
datasize = 2500

preX = input_data.drop('traffic_volume', axis=1).drop('date', axis=1).drop('date_time', axis=1).drop('weather_main',
                                                                                                     axis=1).drop(
    'weather_description', axis=1)
X = preX.iloc[0:datasize]

preY = input_data['traffic_volume']
Y = preY.iloc[0:datasize]

X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.80)

# run k fold cross validation on C value and svc kernel functions 'linear' and 'rbf'
K = 10
Clist = np.power(10, np.linspace(-3, 9, num=7))
k_rankings = np.zeros((K, 3))
error_range = 0.10
rbf = 0
linear = 1
for k in range(0, K):
    x_k_train, x_k_test, y_k_train, y_k_test = train_test_split(X_train, y_train, test_size=0.80)
    max = -math.inf
    bestfun = 0
    bestC = 0
    for fun in range(0, 2):
        for c in range(0, len(Clist)):
            if fun == rbf:
                k_svclassifier = SVC(kernel='rbf', C=Clist[c], gamma='auto')
            else:
                k_svclassifier = SVC(kernel='linear', C=Clist[c], gamma='auto')

            k_svclassifier.fit(x_k_train, y_k_train)
            score = get_score(k_svclassifier, x_k_test, y_k_test, error_range)
            if score > max:
                max = score
                bestfun = fun
                bestC = Clist[c]

    k_rankings[k, 0] = max
    k_rankings[k, 1] = bestfun
    k_rankings[k, 2] = bestC

# find best C and function
best_k = np.argmax(k_rankings[:, 0])
if k_rankings[best_k, 1] == rbf:
    svclassifier = SVC(kernel='rbf', C=k_rankings[best_k, 2], gamma='auto')
else:
    svclassifier = SVC(kernel='linear', C=k_rankings[best_k, 2], gamma='auto')

svclassifier.fit(X_train, y_train)
print("score " + str(get_score(svclassifier, X_test, y_test, error_range)))
print("best function " + str(k_rankings[best_k, 1]))
print("best C " + str(k_rankings[best_k, 2]))
