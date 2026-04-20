import os
import sys

# Suppress logs before any imports
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GRPC_VERBOSITY'] = 'ERROR'
os.environ['GRPC_TRACE'] = ''
os.environ['YDF_VERBOSE'] = '0'
os.environ['ABSL_MIN_LOG_LEVEL'] = '3'

import absl.logging
absl.logging.set_verbosity(absl.logging.FATAL)
absl.logging.use_absl_handler()

from flask import Flask, render_template, request, redirect, url_for, flash
from database import (
    init_db, save_prediction, get_all_predictions,
    get_prediction_stats, delete_prediction,
    clear_all_predictions, search_predictions,
)
from predictor import EnsemblePredictor, extract_all_training_features

app = Flask(__name__)
app.secret_key = 'phishguard-secret-key-change-this'

# Initialize database
init_db()

# Load models once at startup
print("\n🔄 Loading models...")
predictor = EnsemblePredictor({
    'cnn': 'models/cnn_model.joblib',
    'Random Forest': 'models/random_forest_model.joblib',
    'Decision tree': 'models/decision_tree_model.joblib',
})
# predictor = EnsemblePredictor({
#     'CNN': {
#         'path': 'models/best_cnn_model.keras',
#         'type': 'keras',
#     },
#     'Random Forest': {
#         'path': 'models/random_forest_model.joblib',
#         'type': 'joblib',
#     },
#     'Decision Tree': {
#         'path': 'models/decision_tree_model.joblib',
#         'type': 'joblib',
#     },
# })
print("✅ Ready!\n")


@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None

    if request.method == 'POST':
        url = request.form.get('url', '').strip()

        if not url:
            error = "Please enter a valid URL"
        else:
            try:
                features = extract_all_training_features(url)

                if features is None:
                    error = "Could not extract features from this URL"
                else:
                    # ── Pass url for CNN tokenization ──
                    predictions = predictor.predict(features)
                    # print(predictions)
                    if not predictions:
                        error = "No model could make a prediction"
                    else:
                        values = list(predictions.values())
                        final = max(set(values), key=values.count)

                        result = {
                            'url': url,
                            'predictions': predictions,
                            'final': final,
                            'label': 'Phishing' if final == 1 else 'Legitimate',
                        }
                        print(result)
                        save_prediction(url, predictions)

            except Exception as e:
                error = f"Prediction error: {str(e)}"

    stats = get_prediction_stats()
    return render_template('index.html', result=result, error=error, stats=stats)


@app.route('/history')
def history():
    # Search functionality
    search_query = request.args.get('search', '').strip()

    if search_query:
        records = search_predictions(search_query)
    else:
        records = get_all_predictions()

    stats = get_prediction_stats()

    return render_template(
        'history.html',
        history=records,
        stats=stats,
        search_query=search_query,
    )


# @app.route('/delete/<int:pred_id>')
# def delete(pred_id):
#     delete_prediction(pred_id)
#     flash('Record deleted successfully', 'success')
#     return redirect(url_for('history'))


# @app.route('/clear-history')
# def clear_history():
#     clear_all_predictions()
#     flash('All history cleared', 'success')
#     return redirect(url_for('history'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)