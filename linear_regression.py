"""
Script for predicting when the number of dead russian troops will reach 500,000.

Source of data: http://russian-casualties.in.ua/api/v1/data/json/daily
"""
import json
import sys
from datetime import timedelta

import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

N_EXPECTED = 500_000


def predict(dead_russians):
    """
    Predicts numbers of dead russians.
    """
    df = pd.DataFrame(data=dead_russians, columns=["date","pigs"])
    df["date"] = pd.to_datetime(df["date"])
    features = ["year", "month", "day", "weekday", "weekofyear", "quarter"]
    df[features] = df.apply(lambda row: pd.Series({
        "year": row.date.year,
        "month": row.date.month,
        "day": row.date.day,
        "weekday": row.date.weekday(),
        "weekofyear": row.date.weekofyear,
        "quarter": row.date.quarter }), axis=1)

    X = df[features]
    y = df[["pigs"]]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    last_dt = df['date'].iloc[-1]
    result = []
    for i in y_pred:
        dt = "{}.{}.{}".format(last_dt.year, last_dt.month, last_dt.day)
        result.append([dt, i[0]])
        last_dt += timedelta(days=1)
    return result


def calculate():
    #data = json.loads(open('pigs.json').read())

    dead_russians = []
    total_dead_russians = 0
    url = "http://russian-casualties.in.ua/api/v1/data/json/daily"
    response = requests.get(url)
    data = response.json()
    for dt, stuff in data['data'].items():
        dead_russians.append([dt, stuff['personnel']])
        total_dead_russians += stuff['personnel']

    passed_number_of_days = len(dead_russians)

    while True:
        y_pred = predict(dead_russians)

        for i in range(len(y_pred)):
            if (y_pred[i][1] + total_dead_russians) >= N_EXPECTED:
                total_n_days = len(dead_russians) + i
                n_days = total_n_days - passed_number_of_days
                print("{} days ( {:0,.1f} year ) left before {:0,.0f} russians will be dead".format(
                    n_days, n_days / 365., total_dead_russians))
                sys.exit(0)
            total_dead_russians += y_pred[i][1]
        dead_russians.extend(y_pred)


if __name__ == "__main__":
    calculate()
