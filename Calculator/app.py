from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "calculator-secret-key"


def init_db():
    conn = sqlite3.connect("history.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS calculations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expression TEXT,
        result TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET", "POST"])
def calculator():

    expression = ""

    if request.method == "POST":

        expression = request.form.get("expression", "")
        button = request.form.get("button")

        if button == "C":
            expression = ""

        elif button == "=":
            try:
                result = str(eval(expression))

                conn = sqlite3.connect("history.db")
                cur = conn.cursor()

                cur.execute(
                    "INSERT INTO calculations(expression,result) VALUES (?,?)",
                    (expression, result)
                )

                conn.commit()
                conn.close()

                expression = result

            except:
                expression = "Error"

        else:
            expression += button

    conn = sqlite3.connect("history.db")
    cur = conn.cursor()

    cur.execute("""
    SELECT expression, result
    FROM calculations
    ORDER BY id DESC
    LIMIT 10
    """)

    history = cur.fetchall()

    conn.close()

    theme = session.get("theme", "dark")

    return render_template(
        "index.html",
        expression=expression,
        history=history,
        theme=theme
    )


@app.route("/theme/<mode>")
def change_theme(mode):

    themes = ["dark", "light", "blue", "green", "purple"]

    if mode in themes:
        session["theme"] = mode

    return redirect("/")


@app.route("/clear-history")
def clear_history():

    conn = sqlite3.connect("history.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM calculations")

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)