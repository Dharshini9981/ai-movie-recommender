from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Load the trained model and encoders
print("Loading model and encoders...")

with open('model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('encoder.pkl', 'rb') as f:
    data = pickle.load(f)
    encoders = data['encoders']
    features = data['features']
    dataset = data['dataset']

print("Model loaded successfully!")


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    """
    Handle recommendation requests.
    Accepts user preferences and returns top 4 recommendations.
    """
    try:
        # Get user input
        user_input = request.json
        genre = user_input.get('genre')
        mood = user_input.get('mood')
        duration = user_input.get('duration')
        content_type = user_input.get('content_type')
        language = user_input.get('language')

        # Validate input
        if not all([genre, mood, duration, content_type, language]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400

        # Encode user input
        try:
            encoded_input = [
                encoders['genre'].transform([genre])[0],
                encoders['mood'].transform([mood])[0],
                encoders['duration'].transform([duration])[0],
                encoders['content_type'].transform([content_type])[0],
                encoders['language'].transform([language])[0]
            ]
        except ValueError as e:
            return jsonify({'success': False, 'error': f'Invalid input value: {str(e)}'}), 400

        # Convert to numpy array
        X_input = np.array([encoded_input])

        # Get prediction probabilities
        probabilities = model.predict_proba(X_input)[0]

        # Sort all titles by probability (highest first)
        sorted_indices = np.argsort(probabilities)[::-1]

        recommendations = []
        seen_titles = set()

        for idx in sorted_indices:
            title = encoders['title'].inverse_transform([idx])[0]

            # Avoid duplicates
            if title in seen_titles:
                continue

            seen_titles.add(title)
            confidence = probabilities[idx] * 100

            # Get movie/series details from dataset
            movie_data = dataset[dataset['title'] == title].iloc[0]

            # Generate explanation only for top recommendation
            explanation = ""
            if len(recommendations) == 0:
                matches = []

                if movie_data['genre'] == genre:
                    matches.append('genre')
                if movie_data['mood'] == mood:
                    matches.append('mood')
                if movie_data['duration'] == duration:
                    matches.append('duration preference')
                if movie_data['content_type'] == content_type:
                    matches.append('content type')
                if movie_data['language'] == language:
                    matches.append('language')

                if matches:
                    explanation = (
                        f"This was recommended because it matches your selected "
                        f"{', '.join(matches)}. "
                        f"Our Naive Bayes model found it to be the closest fit to your preferences."
                    )
                else:
                    explanation = (
                        "No exact match was found, so this was selected as the best possible recommendation "
                        "based on the overall probability predicted by the Naive Bayes model."
                    )

            recommendations.append({
                'title': title,
                'genre': movie_data['genre'],
                'mood': movie_data['mood'],
                'duration': movie_data['duration'],
                'content_type': movie_data['content_type'],
                'language': movie_data['language'],
                'confidence': round(confidence, 2),
                'explanation': explanation
            })

            # Stop after top 4 recommendations
            if len(recommendations) == 4:
                break

        return jsonify({
            'success': True,
            'recommendations': recommendations
        })

    except Exception as e:
        print(f"Error during recommendation: {str(e)}")
        return jsonify({'success': False, 'error': 'An error occurred during recommendation'}), 500


@app.route('/options', methods=['GET'])
def get_options():
    """Return all available options for dropdowns"""
    options = {
        'genres': sorted(dataset['genre'].unique().tolist()),
        'moods': sorted(dataset['mood'].unique().tolist()),
        'durations': sorted(dataset['duration'].unique().tolist()),
        'content_types': sorted(dataset['content_type'].unique().tolist()),
        'languages': sorted(dataset['language'].unique().tolist())
    }
    return jsonify(options)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)