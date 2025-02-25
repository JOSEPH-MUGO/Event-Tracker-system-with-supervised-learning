import joblib
import pandas as pd
from employee.models import Employee
from EventRecord.models import Event
from django.conf import settings

def load_recommender():
    """
    Load the trained model and the feature preprocessor.
    Adjust the paths as needed (using settings.BASE_DIR is one option).
    """
    # Example: assume these files are in a folder named 'ml_models' at the project root.
    model_path = settings.BASE_DIR / "ml_models/optimized_recommender.pkl"
    preprocessor_path = settings.BASE_DIR / "ml_models/feature_preprocessor.pkl"
    try:
        model = joblib.load(str(model_path))
    except Exception as e:
        raise Exception(f"Failed to load model from {model_path}: {e}")
    try:
        preprocessor = joblib.load(str(preprocessor_path))
    except Exception as e:
        raise Exception(f"Failed to load preprocessor from {preprocessor_path}: {e}")
    return model, preprocessor

def compute_skill_match(event, employee):
    """
    Compute the ratio of required skills (from the event) that the employee possesses.
    """
    # Get skill names for comparison (adjust if your Skills model has different structure)
    event_skills = set(event.required_skills.values_list('name', flat=True))
    employee_skills = set(employee.skills.values_list('name', flat=True))
    if event_skills:
        return len(event_skills.intersection(employee_skills)) / len(event_skills)
    return 0.0

def build_features_for_event(event, employee):
    """
    Build a single-row DataFrame for a given event and employee.
    This row must have the same columns as used in training.

    Expected columns (as per your feature_engineering.py):
      - 'title': the event title (text)
      - 'event_type': the event type (string)
      - 'performance_bin': a binned version of the employee's performance score
      - 'skill_match': computed skill match ratio
      - 'skill_perf_interaction': interaction term between skill match and performance
    """
    # Compute features:
    skill_match = compute_skill_match(event, employee)
    raw_performance = max(employee.performance_score, 60)
    normalized_performance = 60 + (raw_performance - 10)*((100-60) /(100-10))
    computed_bin = int((normalized_performance - 60) // 10)

    # Here we compute a crude performance bin.
    # (Adjust these boundaries to match exactly what you did in training.)
    # For example, if performance scores range from 60 to 100:
    performance_bin = max(computed_bin, 2)  # 60-70:0, 70-80:1, 80-90:2, 90-100:3
    skill_perf_interaction = (skill_match * normalized_performance) / 100.0

    # Build a dictionary of raw features.
    # Note: In training, your preprocessor applied TfidfVectorizer on 'title',
    # one-hot encoding on 'event_type' and 'performance_bin', and passed through numerical features.
    row = {
        "title": event.title,
        "event_type": event.event_type,  # Assuming event_type is stored as a string
        "performance_bin": performance_bin,
        "skill_match": skill_match,
        "skill_perf_interaction": skill_perf_interaction
    }
    return pd.DataFrame([row])

def recommend_employees_for_event(event):
    """
    For a given event, this function builds feature rows for all employees,
    processes them using the saved preprocessor, and then uses the trained model
    to predict which employees are recommended.
    Returns a list of Employee objects.
    """
    model, preprocessor = load_recommender()
    employees = Employee.objects.select_related('admin').prefetch_related('skills').all()
    feature_rows = []
    employee_list = []

    for emp in employees:
        features_df = build_features_for_event(event, emp)
        feature_rows.append(features_df)
        employee_list.append(emp)

    # Combine all rows into a single DataFrame
    all_features = pd.concat(feature_rows, ignore_index=True)

    # Debug: Print the feature DataFrame to verify values
    print("Feature DataFrame:\n", all_features)

    # Transform the features using the preprocessor
    processed_features = preprocessor.transform(all_features)

    # Get predictions from the model (assuming a prediction of 1 indicates a recommendation)
    predictions = model.predict(processed_features)
    recommended = [emp for emp, pred in zip(employee_list, predictions) if pred == 1]
    return recommended
