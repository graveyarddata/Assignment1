## Penguin API

---

This folder contains the Flask-based backend service that loads a trained ML model from google cloud storage (`assignment1group3` bucket) and predicts a penguin species based on four numeric inputs: bill length, bill depth, flipper length, and body mass. The API receives JSON input, runs the model, and returns a JSON response with the predicted species (Adelie, Chinstrap, or Gentoo).