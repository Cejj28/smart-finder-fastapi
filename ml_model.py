"""
ml_model.py
-----------
Loads the pre-trained category classifier (.pkl) at FastAPI startup.
The model is trained by running: python train_model.py
"""

import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "category_model.pkl")

CATEGORIES = [
    "Electronics",
    "Personal Accessories",
    "Bags",
    "Documents",
    "Keys",
    "Clothing",
    "School Supplies",
]


class CategoryModel:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model file not found: category_model.pkl\n"
                "Please run 'python train_model.py' first to generate it."
            )
        self.pipeline = joblib.load(MODEL_PATH)
        print("[OK] Category classifier loaded successfully.")

    def predict(self, item_name: str, description: str = "") -> dict:
        """
        Predicts the category of a lost/found item.

        Args:
            item_name:   The name of the item (e.g. "black wallet")
            description: Optional description for better accuracy

        Returns:
            {
                "category": "Personal Accessories",
                "confidence": 0.94,
                "all_scores": { "Electronics": 0.02, ... }
            }
        """
        # Combine item name and description for richer context
        text = f"{item_name} {description}".strip().lower()

        # Get predicted category
        predicted_category = self.pipeline.predict([text])[0]

        # Get confidence probabilities for all categories
        probabilities = self.pipeline.predict_proba([text])[0]
        class_labels = self.pipeline.classes_

        all_scores = {
            label: round(float(prob), 4)
            for label, prob in zip(class_labels, probabilities)
        }

        # Confidence = probability of the predicted class
        confidence = all_scores[predicted_category]

        return {
            "category": predicted_category,
            "confidence": confidence,
            "all_scores": all_scores,
        }


# Singleton -- loaded once when FastAPI starts
model_instance = CategoryModel()