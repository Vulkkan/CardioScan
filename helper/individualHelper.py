# helper/individualHelper.py
import helper.preprocessor as preprocessor

def get_insights(df):
    insights = []

    if df['fbs_1'].iloc[0] == 1:
        insights.append("Fasting blood sugar is high. Consider reducing sugar intake.")
    elif df['fbs_0'].iloc[0] == 1:
        insights.append("Fasting blood sugar is normal.")

    if df['chol'].iloc[0] > 240:
        insights.append("Cholesterol level is high. Reduce fat intake and exercise.")
    elif df['chol'].iloc[0] < 150:
        insights.append("Cholesterol level is quite low. Add healthy fats to your diet.")

    if df['trestbps'].iloc[0] > 130:
        insights.append("Blood pressure is elevated. Monitor your sodium intake and manage stress.")
    elif df['trestbps'].iloc[0] < 90:
        insights.append("Blood pressure is low. Probably hydrated, and requires a balanced diet.")

    if df['thalach'].iloc[0] < 100:
        insights.append("Heart rate is relatively low. Consider taking cardio exercises.")
    elif df['thalach'].iloc[0] > 180:
        insights.append("Heart rate is quite high. Assessment required.")

    if df['oldpeak'].iloc[0] > 2:
        insights.append("ST depression level is high, which may indicate heart stress. Cardiologist intervention required.")

    if not insights:
        insights.append("Health parameters are within normal ranges. Keep maintaining a healthy lifestyle!")

    return insights



def submitAndPredict(patient, df):
    if df is not None:
        df = preprocessor.encode(df)

        prediction = preprocessor.model.predict(df)
        probabilities = preprocessor.model.predict_proba(df)

        prediction_text = f"{patient} is predicted to be at low risk" if prediction[0] == 1 else f"{patient} is predicted to be at high risk"

        x_prob = f"{probabilities[0][1] * 100:.2f}%"
        y_prob = f"{probabilities[0][0] * 100:.2f}%"

        insights = get_insights(df)

        return patient, prediction_text, x_prob, y_prob, insights
    
    else:
        return None
