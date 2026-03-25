import pandas as pd
import pickle
import numpy as np
from sklearn.naive_bayes import CategoricalNB
from sklearn.preprocessing import LabelEncoder

def train_recommendation_model():
    """
    Train a Naive Bayes model for movie/series recommendation
    using the movies.csv dataset
    """
    print("Loading dataset...")

    # Load dataset
    df = pd.read_csv('movies.csv')
    print(f"Dataset loaded with {len(df)} entries")

    # Create encoders
    encoders = {}
    encoded_data = {}

    # Feature columns
    features = ['genre', 'mood', 'duration', 'content_type', 'language']

    print("Encoding categorical features...")
    for feature in features:
        encoder = LabelEncoder()
        encoded_data[feature] = encoder.fit_transform(df[feature])
        encoders[feature] = encoder

    # Encode target column (title)
    title_encoder = LabelEncoder()
    encoded_titles = title_encoder.fit_transform(df['title'])
    encoders['title'] = title_encoder

    # Prepare X and y
    X = np.column_stack([encoded_data[feature] for feature in features])
    y = encoded_titles

    print("Training Categorical Naive Bayes model...")

    # Train model
    model = CategoricalNB()
    model.fit(X, y)

    print("Saving model and encoders...")

    # Save model
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)

    # Save encoders + dataset
    with open('encoder.pkl', 'wb') as f:
        pickle.dump({
            'encoders': encoders,
            'features': features,
            'dataset': df
        }, f)

    print("Model training complete!")
    print("Model saved to: model.pkl")
    print("Encoders saved to: encoder.pkl")

    # Show training accuracy
    accuracy = model.score(X, y)
    print(f"Training accuracy: {accuracy * 100:.2f}%")

if __name__ == "__main__":
    train_recommendation_model()