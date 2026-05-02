from transformers import pipeline

class Model:
    def __init__(self):
        # Loads pretrained sentiment model automatically
        self.classifier = pipeline("sentiment-analysis") # [cite: 38, 41]

    def predict(self, text: str):
        result = self.classifier(text)[0] # [cite: 43]
        return {
            "label": result["label"], # [cite: 45]
            "score": float(result["score"]) # [cite: 46]
        }

model_instance = Model() # [cite: 47]