# ===== API FILE =====
# Purpose: receive 4 numbers, load model (from GCS in prod), return JSON {"species":"Adelie"}

# importing Flask and other modules
from flask import Flask, request, jsonify

# Flask constructor
app = Flask(__name__)

# A decorator used to tell the application which URL is associated with the function
@app.route('/what_penguin_are_you', methods=["GET", "POST"])
def check_penguin():
    if request.method == "GET":
        return render_template("input_form_page.html")

    elif request.method == "POST":
        bl = int(request.form.get("bl"))  # getting input with name = bl from HTML form
        bd = int(request.form.get("bd"))
        fl = int(request.form.get("fl"))
        bm = int(request.form.get("bm"))

        # ==== REPLACE FROM HERE WITH ML PREDICTION MODEL!!!

        if pgc > 120: # the prediction variable needs to be output 'Adelie', 'Chinstrap', or 'Gentoo'
            prediction_value = True
        else:
            prediction_value = False

        # leave this to render the response page with the prediction_value set in code above
        return render_template("response_page.html",
                               prediction_variable=prediction_value) # the prediction variable needs to be output 'Adelie', 'Chinstrap', or 'Gentoo'

        # ==== REPLACE UNTIL HERE WITH ML PREDICTION MODEL!!!
    else:
        return jsonify(message="Method Not Allowed"), 405
    # The 405 Method Not Allowed indicates that the app does not allow the users to perform any other HTTP method (e.g., PUT and  DELETE) for
    # '/what_penguin_are_you' path


# The code within this conditional block will only run the python file is executed as a
# script. See https://realpython.com/if-name-main-python/
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
