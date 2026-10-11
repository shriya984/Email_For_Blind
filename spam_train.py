import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json

# ---------- STEP 1: Load and prepare data ----------
# Fix encoding issue
df = pd.read_csv("C:\\Users\\shriy\\OneDrive\\Pictures\\Desktop\\spam.csv", encoding='latin-1')

# Keep only needed columns (some spam datasets have extra columns)
df = df[['v1', 'v2']]
df.columns = ['label', 'text']

# Convert labels to 0 = ham, 1 = spam
df['label_num'] = df['label'].map({'ham': 0, 'spam': 1})

# ---------- STEP 2: Split into train/test ----------
X_train, X_test, y_train, y_test = train_test_split(
    df['text'], df['label_num'], test_size=0.2, random_state=42
)

# ---------- STEP 3: Convert text to TF-IDF features ----------
vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

# ---------- STEP 4: Train Naïve Bayes model ----------
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)

# ---------- STEP 5: Evaluate accuracy ----------
train_pred = model.predict(X_train_tfidf)
test_pred = model.predict(X_test_tfidf)

train_acc = accuracy_score(y_train, train_pred) * 100
test_acc = accuracy_score(y_test, test_pred) * 100

print(f"Training Accuracy: {train_acc:.2f}%")
print(f"Testing Accuracy: {test_acc:.2f}%\n")

# Classification Report
print("Classification Report:\n", classification_report(y_test, test_pred))

# ---------- STEP 6: Confusion Matrix ----------
cm = confusion_matrix(y_test, test_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Ham', 'Spam'], yticklabels=['Ham', 'Spam'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# ---------- STEP 7: Accuracy Graph ----------
plt.figure(figsize=(5,4))
plt.bar(['Training Accuracy', 'Testing Accuracy'], [train_acc, test_acc], color=['green','orange'])
plt.title('Spam Filter Accuracy Comparison')
plt.ylabel('Accuracy (%)')
plt.ylim(0, 100)
plt.show()

# ---------- STEP 8: Save model and vectorizer ----------
joblib.dump(model, "spam_model.pkl")
joblib.dump(vectorizer, "tfidf_vectorizer.pkl")
print("\n✅ Model and vectorizer saved successfully!")

# ---------- STEP 9: Export top spam keywords for PHP ----------
# Compute keyword spam scores from trained model
feature_names = vectorizer.get_feature_names_out()
spam_scores = model.feature_log_prob_[1] - model.feature_log_prob_[0]  # log(P(word|spam)) - log(P(word|ham))
keyword_scores = {feature_names[i]: float(spam_scores[i]) for i in range(len(feature_names))}

# Save as JSON
with open("spam_keywords.json", "w") as f:
    json.dump(keyword_scores, f, indent=2)

print("✅ spam_keywords.json exported for PHP use!")
