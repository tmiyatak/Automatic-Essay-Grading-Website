from flask import Flask
from flask import jsonify, request
import pandas as pd
from sklearn.preprocessing import Imputer
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import TIdatabase as ti

app = Flask(__name__)
clf = None
predictor_cols = ["admissionstest","AP","averageAP","SATsubject","GPA","schooltype",
                  "intendedgradyear","female","MinorityRace","international","sports",
                  "earlyAppl","alumni","outofstate","acceptrate","size","public",
                  "finAidPct","instatePct"]
NUM_ESTIMATORS = 50

colleges = ti.College()

def load_classifier():
    global clf
    df = pd.read_csv("collegedata_normalized.csv")
    cols_to_drop = []
    for i in df.columns:
        if 1.0* df[i].isnull().sum() / len(df[i]) >= 0.5:
            cols_to_drop.append(i)
    dfr = df.drop(cols_to_drop,axis=1)
    dfr = dfr[pd.notnull(df["acceptStatus"])]
    dfpredict = dfr[predictor_cols]
    dfresponse = dfr["acceptStatus"]
    imp = Imputer(missing_values="NaN", strategy="median", axis=1)
    imp.fit(dfpredict)
    X = imp.transform(dfpredict)
    y = dfresponse
    clf = RandomForestClassifier(n_estimators=NUM_ESTIMATORS)
    clf.fit(X,y)

def genPredictionList(vals):
    global predictor_cols
    preds = []
    X = np.array(vals)
    for i, row in colleges.df.iterrows():
        y = clf.predict_proba(X)[0][1]
        p = {'college':row.collegeID, 'prob':y}
        preds.append(p)
    return preds
    #g = [{'college':'harvard', 'prob':y}, {'college':'yale', 'prob':0.25}, {'college':'brown', 'prob':0.89}]


@app.route("/")
def hello():
    return "Welcome to the Team Ivy Web Service"

@app.route("/predict")
def predict():
    vals = []
    for i in predictor_cols:
        vals.append( float(request.args.get(i)))
    preds = genPredictionList(vals)
    return jsonify(preds = preds)

if __name__ == "__main__":
    load_classifier()
    app.run(debug=True)
