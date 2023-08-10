import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    users = db.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])
    owned_cash = users[0]["cash"]
    stocks = db.execute(
        "SELECT symbol, name, price, SUM(shares) as totalShares FROM purchases WHERE user_id = ? GROUP BY symbol",
        session["user_id"],
    )
    return render_template("index.html", stocks=stocks, owned_cash=owned_cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        sharez = request.form.get("shares")
        try:
            shar = int(sharez)
        except ValueError:
            return apology("INVALID SHARES")
        if float(sharez) < 1:
            return apology("Please input a valid number")
        my_dict = lookup(request.form.get("symbol"))
        # Ensure valid symbol
        if not my_dict:
            return apology("Stock Quote not found")
        # Ensure if there is enough cash
        tprice = my_dict["price"] * float(request.form.get("shares"))
        usercash = float(
            db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0][
                "cash"
            ]
        )
        if tprice > usercash:
            return apology("Not enough cash")
        # Now there is enough cash and valid input, time to buy it
        db.execute(
            "INSERT INTO purchases (user_id, name, shares, price, type, symbol) VALUES (?,?,?,?,?,?)",
            session["user_id"],
            my_dict["name"],
            float(request.form.get("shares")),
            float(my_dict["price"]),
            "buy",
            request.form.get("symbol"),
        )
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?",
            usercash - tprice,
            session["user_id"],
        )
        flash("Bought!")
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    stocks = db.execute("SELECT symbol,shares,price,time FROM purchases")
    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        my_dict = lookup(request.form.get("symbol"))
        if my_dict:
            return render_template("quoted.html", my_dict=my_dict)
        else:
            return apology("Stock Quote not found")
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password is the same with confirmation
        elif request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords must match", 400)
        # Ensure username is not taken
        taken = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(taken) == 1:
            return apology("username taken", 400)
        else:
            db.execute(
                "INSERT INTO users (username, hash) VALUES (?,?)",
                request.form.get("username"),
                generate_password_hash(request.form.get("password")),
            )
            return render_template("login.html")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        names = db.execute("SELECT DISTINCT symbol FROM purchases")
        return render_template("sell.html", names=names)
    else:
        sembol = request.form.get("symbol")
        share = request.form.get("shares")
        sum_shares = db.execute(
            "SELECT SUM(shares) as total FROM purchases WHERE user_id = ? AND symbol = ? GROUP BY name",
            session["user_id"],
            sembol,
        )
        if int(sum_shares[0]["total"]) < int(share):
            return apology("Invalid Share")
        # Execute a transaction
        my_dict = lookup(request.form.get("symbol"))
        db.execute(
            "INSERT INTO purchases (user_id, name, shares, price, type, symbol) VALUES(?, ?, ?, ?, ? ,?);",
            session["user_id"],
            my_dict["name"],
            -int(share),
            int(share) * my_dict["price"],
            "sell",
            sembol,
        )

        # Update user owned cash
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?;",
            (rows[0]["cash"] + (my_dict["price"] * int(share))),
            session["user_id"],
        )

        flash("Sold!")
        return redirect("/")
