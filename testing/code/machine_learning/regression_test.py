import numpy as np
from sklearn.linear_model import LinearRegression

X = np.array([[1], [2], [3], [4], [5]])
y = np.array([1.5, 3.1, 4.5, 6.2, 7.9])

model = LinearRegression()
model.fit(X, y)

predictions = model.predict(X)

print(predictions)