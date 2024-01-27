import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from joblib import dump, load

def train():
    data = pd.read_csv('./data.csv', delimiter=',')

    X_train, X_test, y_train, y_test = train_test_split(
                                            data[['Temp[C]', 'Rain[mm]', 'Day', 'Month', 'DayOfWeek', 'IsHoliday']].values,
                                            data['Passangers'].values, 
                                            test_size=0.20
                                            )

    # Standardize the features to have mean=0 and variance=1
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Create MLPRegressor object
    model = MLPRegressor(hidden_layer_sizes=(250, 200, 150, 20), activation='relu', solver='adam', max_iter=2000, batch_size=32)

    model.fit(X_train_scaled, y_train)
    #dump(model, './weights/model_weights.joblib')
    #dump(scaler, './weights/scaler.joblib')
    y_pred = model.predict(X_test_scaled)

    score = model.score(X_test_scaled, y_test)
    mse = np.sqrt(mean_squared_error(y_test, y_pred))

    # save settings to csv to track progress
    if os.stat('./model_settings.csv').st_size == 0:
        with open('./model_settings.csv', 'a') as f:
            f.write('hidden_layer_sizes,activation,solver,max_iter,batch_size, score, mse, coefficient\n')

    # Append the model settings
    with open('./model_settings.csv', 'a') as f:
        f.write(f'{model.hidden_layer_sizes},{model.activation},{model.solver},{model.max_iter},')
        f.write(f'{model.batch_size},{score}, {mse}, {r2_score(y_test, y_pred)}\n')

    print('Model determination: ', score)
    print(f'Mean squared error: {mse:3.3} ({mse/np.mean(y_pred)*100:3.3}%)')
    print('Coefficient of determination: %.2f' % r2_score(y_test, y_pred))

    # Plot outputs
    plt.scatter(X_test[:,0], y_test,  color='black')
    plt.scatter(X_test[:,0], y_pred, color='blue', linewidth=3)
    plt.xticks(())
    plt.yticks(())
    plt.show()


def predict_passangers(temp, rain, day, month, day_of_week, is_holiday):
    """
    temp: float (C)
    rain: float (mm)
    day: int (1-31)
    month: int (1-12)
    day_of_week: int 0-6 (Monday-Sunday)
    is_holiday: int (0 or 1) (False or True)
    returns: int (passangers)
    """
    path = os.path.dirname(os.path.abspath(__file__))
    model = load(path + '/weights/model_weights.joblib')
    scaler = load(path + '/weights/scaler.joblib')
    X = scaler.transform([[temp, rain, day, month, day_of_week, is_holiday]])
    return model.predict(X)[0]
