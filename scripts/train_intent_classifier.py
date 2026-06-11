from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


DATA_PATH = Path("data/training/intent_training.csv")
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "intent_classifier.joblib"


def train_intent_classifier() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Training data not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    if "text" not in df.columns or "intent" not in df.columns:
        raise ValueError("Training CSV must contain columns: text,intent")

    x = df["text"].astype(str)
    y = df["intent"].astype(str)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    model = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("Intent classifier trained successfully.")
    print(f"Saved model to: {MODEL_PATH}")
    print(f"Test accuracy: {accuracy:.3f}")
    print()
    print(classification_report(y_test, predictions))


if __name__ == "__main__":
    train_intent_classifier()