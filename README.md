# Finance-cs50
A web app for managing a stock portfolio and making transactions

**Project for Week 8 of Harvard's CS50**

[View the full assignment description](https://cs50.harvard.edu/x/2020/tracks/web/finance/)

Briefly, the task was to make a web app via which you can manage portfolios of stocks. This web app will allow you to check real stocks’ actual prices and portfolios’ values. It will also let you buy and sell stocks listed in the New York Stock Exchange (NYSE) by querying IEX's API.

## Technologies
* Python
* Flask with session authentication
* SQLite3
* HTML

## What I've done

I've completed register, index, buy, sell, history and quote functions at app.py by using **python, flask and sql** ,and wrote all the html files except login and layout in the templates folder by using **html and jinja**

### Register
Allow a new user to register for an account, rendering an apology view if the form data is incomplete or if the username already exists in the database.
![alt text](https://github.com/OnurAltayTopaloglu/finance-cs50x/blob/main/static/register_img.png)

### Buy
Allows the user to "buy" stocks by submitting a form with the stock's symbol and number of shares. Checks to ensure the stock symbol is valid and the user can afford the purchase at the stock's current market price with their available balance, and stores the transaction history in the database.
![alt text]()

### Index
The homepage displays a table of the logged-in user's owned stocks, number of shares, current stock price, value of each holding. This view also shows the user's imaginary "cash" balance and the total of their "cash" plus stock value.
![alt text]()

### Quote
Allows the user to submit a form to look up a stock's current price, retrieving real-time data from the IEX API. An error message is rendered if the stock symbol is invalid.
![alt text]()



### Sell
Allows the user to "sell" shares of any stock currently owned in their portfolio. 
![alt text]()

### History
Displays a table summarizing the user's past transactions (all buys and sells). Each row in the table lists whether the stock was bought or sold, the stock's symbol, the buy/sell price, the number of shares, and the transaction's date/time.
![alt text]()

