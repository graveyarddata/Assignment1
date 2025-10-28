## Penguin UI

---
The penguin_app_ui.py file hosts the user interface of the application. It serves the HTML form (`input_form_page.html`) where users enter penguin measurements (`bill length`, `bill depth`, `body mass`, and `body mass`) and sends these values to the prediction API endpoint (`/predict`).
The API returns one of three species — **Adelie, Chinstrap, or Gentoo** — which is displayed on the `response_page.html`.
