## Penguin UI

---
The penguin_app_ui.py file hosts the user interface of the application. It serves the HTML form (`input_form_page.html`) where users enter penguin measurements (`bill length`, `bill depth`, `body mass`, and `body mass`) and sends these values to the prediction API endpoint (`/predict`).
The API returns one of three species — **Adelie, Chinstrap, or Gentoo** — which is displayed on the `response_page.html`.

The base URL for the API (`PREDICTOR_API`) is automatically set by **Cloud Build/Run** during deployment, or will default to http://127.0.0.1:5000 for local testing.