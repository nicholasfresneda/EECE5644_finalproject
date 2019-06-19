import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC, SVR
import math
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix


# find score of a classifier
# compares predicted traffic volume to real traffic volume, if within 5% of real, it is deemed correct
# arguments:
#   pred = predictions
#   ytest = real values
#   error = percent allowable error
def get_score(pred, ytest, error):
    count = 0
    for i in range(0, len(y_pred)):
        delta = ytest.iloc[i] * error
        if ytest.iloc[i] - delta < pred[i] < ytest.iloc[i] + delta:
            count = count + 1

    return count / len(y_pred)


# get data from csv
traffic_column = 8
input_data = pd.read_csv("CleanedData.csv")
datasize = 1000

# split data into training and test sets
preX = input_data.drop('traffic_volume', axis=1).drop('date', axis=1).drop('date_time', axis=1).drop('weather_main',  axis=1).drop('weather_description', axis=1)
X = preX.iloc[0:datasize]
preY = input_data['traffic_volume']
Y = preY.iloc[0:datasize]
X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.30)

# run k fold cross validation on C value and svc kernel functions 'linear' and 'rbf'
K = 10
Clist = np.power(10, np.linspace(-3, 9, num=7))
k_rankings = np.zeros((K, 3))
error_range = 0.10
rbf = 0
linear = 1
scores = np.zeros((len(Clist), 2))
for k in range(0, K):
    x_k_train, x_k_test, y_k_train, y_k_test = train_test_split(X_train, y_train, test_size=0.30)
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
            y_pred = k_svclassifier.predict(x_k_test)
            score = get_score(y_pred, y_k_test, error_range)
            scores[c, fun] = score
            if score > max:
                max = score
                bestfun = fun
                bestC = Clist[c]

    k_rankings[k, 0] = max
    k_rankings[k, 1] = bestfun
    k_rankings[k, 2] = bestC


# graph k fold validation
plt.figure(1)
plt.plot(Clist, scores[:, 1], 'bo', label = 'linear')
plt.plot(Clist, scores[:, 0], 'ro', label = 'rbf')
plt.legend(loc='upper left')
# find best C and function
best_k = np.argmax(k_rankings[:, 0])
if k_rankings[best_k, 1] == rbf:
    svclassifier = SVC(kernel='rbf', C=k_rankings[best_k, 2], gamma='auto')
else:
    svclassifier = SVC(kernel='linear', C=k_rankings[best_k, 2], gamma='auto')

# fit classifier to training data and test
svclassifier.fit(X_train, y_train)
y_pred = svclassifier.predict(X_test)
print("Predictions correct within 10% margin " + str(get_score(y_pred, y_test, error_range)))
print("best function " + str(k_rankings[best_k, 1]))
print("best C " + str(k_rankings[best_k, 2]))
print("mean squared error " + str(mean_squared_error(y_test, y_pred)))
# export to new csv
new_df = X_test
new_df.insert(traffic_column, "traffic_volume", y_test)
new_df.insert(len(new_df.columns), "predictions", y_pred)
new_df.to_csv("results.csv")

# plot data
plt.figure(2)
plt.plot(y_test, y_pred, 'o', alpha=0.3)
plt.plot([0, 7000], [0, 7000], color="orange")
plt.show()

percents = np.zeros(100)
for i in range(0, 100):
    percents[i] = get_score(y_pred, y_test, i * 0.01)

x_axis = np.linspace(0, 100, 100)
plt.figure(3)
plt.plot(x_axis, percents)
plt.show()
