from flask import Flask, render_template, request, redirect, session, url_for
import requests
import json


def load_users():
    try:
        with open('db.json', 'r') as file:
            users_data = json.load(file)
            return users_data.get('users', {})
    except FileNotFoundError:
        return {}


class CurrencyConverter:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'supersecretkey'
        self.data = requests.get('https://api.exchangerate-api.com/v4/latest/USD').json()
        self.currencies = self.data['rates']
        self.users = load_users()

        @self.app.route("/", methods=['GET', 'POST'])
        def currency_converter():
            if 'username' in session:
                username = session['username']
                if request.method == "POST":
                    from_currency = request.form['from-currency']
                    to_currency = request.form['to-currency']
                    amount = float(request.form['amount'])
                    result = self.convert(from_currency, to_currency, amount)
                    return render_template("index.html", fromCurrency=from_currency, toCurrency=to_currency,
                                           amount=amount, result=result, currencies=self.currencies)
                return render_template("index.html", currencies=self.currencies, username=username)
            else:
                return redirect(url_for('login'))

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                if username in self.users and self.users[username]['password'] == password:
                    session['username'] = username
                    return redirect(url_for('currency_converter'))
                else:
                    return render_template('login.html', message='Invalid username or password')
            return render_template('login.html', message='')

        @self.app.route('/logout')
        def logout():
            session.pop('username', None)
            return redirect(url_for('login'))

    def convert(self, from_currency, to_currency, amount):
        if self.currencies:
            return round(amount / self.currencies[from_currency] * self.currencies[to_currency], 5)

    def run(self):
        self.app.run(debug=True)


if __name__ == '__main__':
    converter = CurrencyConverter()
    converter.run()
