from application import app
from flask import render_template, redirect, flash, url_for, request

@app.route("/")
@app.route("/index")
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]

    return render_template("index.html", title="Home", posts=posts)
