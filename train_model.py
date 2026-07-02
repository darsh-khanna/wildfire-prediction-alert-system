import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, precision_recall_curve, average_precision_score
import joblib
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv('natural_disasters.csv')

# Filter only Wildfire rows and extract relevant features
wildfire_df = df[df['Disaster_Type'].str.lower().str.contains('fire|wildfire')].copy()

# Extract features - including the new Pollution Level (AQI)
features = ['Temperature (°C)', 'Humidity Level (%)', 'Pollution Level (AQI)']
wildfire_df = wildfire_df[features].dropna()

# Create binary label (1 for wildfire, 0 for non-wildfire conditions)
non_wildfire_df = df[~df['Disaster_Type'].str.lower().str.contains('fire|wildfire')].copy()
non_wildfire_df = non_wildfire_df[features].dropna()

# Create balanced samples (2:1 ratio of non-wildfire to wildfire samples)
non_wildfire_sample = non_wildfire_df.sample(n=len(wildfire_df)*2, random_state=42)

# Assign labels (1 for wildfire, 0 for non-wildfire)
wildfire_df['Wildfire'] = 1
non_wildfire_sample['Wildfire'] = 0

# Combine the datasets
combined_df = pd.concat([wildfire_df, non_wildfire_sample])

# Add feature interactions
combined_df['Temp_Humidity_Interaction'] = combined_df['Temperature (°C)'] * (100 - combined_df['Humidity Level (%)'])
combined_df['Temp_AQI_Interaction'] = combined_df['Temperature (°C)'] * combined_df['Pollution Level (AQI)']

# Update features list
features = ['Temperature (°C)', 'Humidity Level (%)', 'Pollution Level (AQI)',
           'Temp_Humidity_Interaction', 'Temp_AQI_Interaction']

# Features and label
X = combined_df[features]
y = combined_df['Wildfire']

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Train model with improved parameters
model = RandomForestClassifier(
    random_state=42,
    class_weight='balanced',
    n_estimators=200,
    max_depth=10,
    min_samples_split=5
)
model.fit(X_train, y_train)

# Evaluate model
print("Evaluation Results:")
print(classification_report(y_test, model.predict(X_test)))

# Additional metrics
precision, recall, thresholds = precision_recall_curve(y_test, model.predict_proba(X_test)[:, 1])
ap_score = average_precision_score(y_test, model.predict_proba(X_test)[:, 1])
print(f"\nAverage Precision Score: {ap_score:.4f}")

# Feature importance
print("\nFeature Importances:")
for feature, importance in zip(features, model.feature_importances_):
    print(f"{feature}: {importance:.4f}")

# Visualize feature importances
plt.figure(figsize=(10, 6))
plt.barh(features, model.feature_importances_)
plt.title('Feature Importances')
plt.tight_layout()
plt.savefig('feature_importances.png')
plt.close()

# Save model
joblib.dump(model, 'wildfire_model.pkl')
print("\nModel saved as wildfire_model.pkl")