import joblib
import pandas as pd
from employee.models import Employee
from EventRecord.models import Event
from django.conf import settings

def load_recommender():
   
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
    
    
    event_skills = set(event.required_skills.values_list('name', flat=True))
    employee_skills = set(employee.skills.values_list('name', flat=True))
    if event_skills:
        return len(event_skills.intersection(employee_skills)) / len(event_skills)
    return 0.0

def build_features_for_event(event, employee):
   
    # Computing features:
    skill_match = compute_skill_match(event, employee)
    raw_performance = max(employee.performance_score, 60)
    normalized_performance = 60 + (raw_performance - 10)*((100-60) /(100-10))
    computed_bin = int((normalized_performance - 60) // 10)

    
    performance_bin = max(computed_bin, 2)  
    skill_perf_interaction = (skill_match * normalized_performance) / 100.0

 
    row = {
        "title": event.title,
        "event_type": event.event_type,  
        "performance_bin": performance_bin,
        "skill_match": skill_match,
        "skill_perf_interaction": skill_perf_interaction
    }
    return pd.DataFrame([row])

def recommend_employees_for_event(event):
    """
    this function builds a feature rows for all employees for a given event,
    processes them using the saved preprocessor, and then uses the trained model
    to predict which employees are recommended.
    """
    model, preprocessor = load_recommender()
    employees = Employee.objects.select_related('admin').prefetch_related('skills').all()
    feature_rows = []
    employee_list = []

    for emp in employees:
        features_df = build_features_for_event(event, emp)
        feature_rows.append(features_df)
        employee_list.append(emp)

    # Combining all rows into a single DataFrame
    all_features = pd.concat(feature_rows, ignore_index=True)

    #Printing the feature DataFrame to verify values
    print("Feature DataFrame:\n", all_features)

    # Transforming features using the preprocessor
    processed_features = preprocessor.transform(all_features)

    # Get predictions from the model if predictions == 1)
    predictions = model.predict(processed_features)
    recommended = [emp for emp, pred in zip(employee_list, predictions) if pred == 1]
    return recommended
