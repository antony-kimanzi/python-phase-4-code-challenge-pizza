#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.errorhandler(ValueError)
def handle_value_error(error):
    response = jsonify({"errors": [str(error)]})
    response.status_code = 400
    return response

# @app.errorhandler(KeyError)
# def handle_value_error(error):
#     response = jsonify({"error": str(error)})
#     response.status_code = 400
#     return response


@app.route("/")
def index():
    return "<h1>Code challenge</h1>", 200


@app.route("/restaurants")
def all_restaurants():
    restaurants = Restaurant.query.all()

    if restaurants:
        restaurant_list = [
            {"address": restaurant.address, "id": restaurant.id, "name": restaurant.name}
            for restaurant in restaurants
        ]
        return make_response(jsonify(restaurant_list), 200)
    else:
        return jsonify({"error": "No restaurants found"}), 404


@app.route("/restaurants/<int:id>")
def single_restaurant(id):
    restaurant =db.session.get(Restaurant, id)

    if restaurant:
        restaurantpizzas = restaurant.restaurantpizza
        restaurantpizza_list = [
            {
                "id": restaurantpizza.id,
                "pizza": {
                    "id": restaurantpizza.pizza.id,
                    "ingredients": restaurantpizza.pizza.ingredients,
                    "name": restaurantpizza.pizza.name,
                },
                "pizza_id": restaurantpizza.pizza_id,
                "price": restaurantpizza.price,
                "restaurant_id": restaurantpizza.restaurant_id,
            }
            for restaurantpizza in restaurantpizzas
        ]

        return jsonify(
            {
                "address": restaurant.address,
                "id": restaurant.id,
                "name": restaurant.name,
                "restaurant_pizzas": restaurantpizza_list,
            }
        ), 200
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant =db.session.get(Restaurant,id)

    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return make_response("", 204)
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route("/pizzas")
def fetch_pizzas():
    pizzas = Pizza.query.all()

    if pizzas:
        pizzas_list = [
            {"id": pizza.id, "ingredients": pizza.ingredients, "name": pizza.name}
            for pizza in pizzas
        ]

        return jsonify(pizzas_list), 200
    else:
        return jsonify({"error": "No pizzas found"}), 404


@app.route("/restaurant_pizzas", methods=["POST"])
def add_retaurantpizza():
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    check_pizza = Pizza.query.filter_by(id=pizza_id).first()
    check_restaurant = Restaurant.query.filter_by(id=restaurant_id).first()

    if check_pizza and check_restaurant:
            
        new_restaurantpizza = RestaurantPizza(
            price=price, pizza_id=pizza_id, restaurant_id=restaurant_id
        )
        db.session.add(new_restaurantpizza)
        db.session.commit()

        restaurant_pizza = RestaurantPizza.query.filter_by(
            price=price, pizza_id=pizza_id, restaurant_id=restaurant_id
        ).first()

        return jsonify(
            {
                "id": restaurant_pizza.id,
                "pizza": {
                    "id": restaurant_pizza.pizza.id,
                    "ingredients": restaurant_pizza.pizza.ingredients,
                    "name": restaurant_pizza.pizza.name,
                },
                "pizza_id": restaurant_pizza.pizza_id,
                "price": restaurant_pizza.price,
                "restaurant": {
                    "address": restaurant_pizza.restaurant.address,
                    "id": restaurant_pizza.restaurant.id,
                    "name": restaurant_pizza.restaurant.name,
                },
                "restaurant_id": restaurant_pizza.restaurant_id,
            }
        ), 201
    else:
        # Return validation errors for missing pizza or restaurant
        return jsonify({"error": "Unable to add restaurant_pizza"}), 400

#### additional endpoints ####


@app.route("/add/restaurant", methods=["POST"])
def add_restaurant():
    data = request.get_json()

    name = data["name"]
    address = data["address"]

    check_name = Restaurant.query.filter_by(name=name).first()
    check_address = Restaurant.query.filter_by(address=address).first()

    if not check_name and not check_address:
        new_restaurant = Restaurant(name=name, address=address)
        db.session.add(new_restaurant)
        db.session.commit()

        return jsonify({"success": "Restaurant added successfully"}), 201
    else:
        return jsonify({"error": "Unable to add restaurant"}), 400


@app.route("/add/pizza", methods=["POST"])
def add_pizza():
    data = request.get_json()

    name = data["name"]
    ingredients = data["ingredients"]

    check_name = Pizza.query.filter_by(name=name).first()

    if not check_name:
        new_pizza = Pizza(name=name, ingredients=ingredients)
        db.session.add(new_pizza)
        db.session.commit()

        return jsonify({"success": "Pizza added successfully"}), 201
    else:
        return jsonify({"error": "Unable to add pizza"}), 400
    
@app.route("/delete/restaurant_pizzas/<int:id>", methods=["DELETE"])
def delete_restaurant_pizza(id):
    restaurantpizza = RestaurantPizza.query.get(id)

    if restaurantpizza:
        db.session.delete(restaurantpizza)
        db.session.commit()
        return make_response("", 204)
    else:
        return jsonify({"error": "Restaurant pizza not found"}), 404


if __name__ == "__main__":
    app.run(port=5555, debug=True)
