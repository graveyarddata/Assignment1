# ===== UI FILE =====

# importing Flask and other modules
from flask import Flask, request, render_template, jsonify
import os, requests

# Flask constructor with link to html pages
app = Flask(__name__, template_folder='html form and response pages')

# Cloud Build/Run will inject this env to point at the API service URL (and will otherwise run locally)
PREDICTOR_API = os.getenv("PREDICTOR_API", "http://127.0.0.1:5000")

# A decorator used to tell the application which URL is associated with the function
@app.route('/what_penguin_are_you', methods=["GET", "POST"])
def what_penguin():
    if request.method == "GET":
        return render_template("input_form_page.html")

    elif request.method == "POST":
        bl = float(request.form.get("bl"))  # getting input with name = bl from HTML form
        bd = float(request.form.get("bd"))
        fl = float(request.form.get("fl"))
        bm = float(request.form.get("bm"))

        # Put the payload in a JSON file for the API
        payload = {
            "bill_length_mm": bl,
            "bill_depth_mm": bd,
            "flipper_length_mm": fl,
            "body_mass_g": bm
        }

        # ---- CALL THE API (connection to ML prediction) ----
        try:
            r = requests.post(f"{PREDICTOR_API}/predict", json=payload)
            r.raise_for_status() # will give an error if the API is down
            species = r.json()["species"] # model will return Adelie/Chinstrap/Gentoo
        except Exception as e:
            species = f"Error: {e}"
        return render_template("response_page.html", prediction_variable=species)

        # --- END OF API CALL -----
    else:
        return jsonify(message="Method Not Allowed"), 405
    # The 405 Method Not Allowed indicates that the app does not allow the users to perform any other HTTP method (e.g., PUT and  DELETE) for
    # '/what_penguin_are_you' path

# The code within this conditional block will only run the python file is executed as a
# script. See https://realpython.com/if-name-main-python/
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
