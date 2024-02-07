from flask import render_template

from src.restaurant_hub.application.controller import main


@main.route('/', methods=['GET'])
def load_index():
    return render_template('index.html')
