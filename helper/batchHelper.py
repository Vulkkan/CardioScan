# helper/batchHelper.py
from helper import preprocessor, individualHelper

def submitAndPredictBatch(data):
    if data is not None:
        model = preprocessor.model
        df = data

        patients, df = preprocessor.encodeBatch(df)

        predictions = model.predict(df)
        probabilities = model.predict_proba(df)
        results = []

        for i in range(len(df)):
            prediction = f"{patients[i]} is predicted to be at low risk" if predictions[i] == 1 else f"{patients[i]} is predicted to be at high risk"

            insights = individualHelper.get_insights(df.iloc[[i]])

            x_prob = probabilities[i][1] * 100
            y_prob = probabilities[i][0] * 100
            
            results.append({
                "Patient": patients[i],
                "Prediction": prediction,
                "X_Probability": x_prob,
                "Y_Probability": y_prob,
                "Insights": insights
            })

        return results
