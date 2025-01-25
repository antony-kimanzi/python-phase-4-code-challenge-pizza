from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

# Custom metadata for database naming conventions
metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)


# Restaurant Model
class Restaurant(db.Model, SerializerMixin):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)

    # Relationships
    restaurantpizza = db.relationship(
        "RestaurantPizza",
        back_populates="restaurant",
        cascade="all, delete-orphan"  # Cascade deletes
    )

    # Serialization rules
    serialize_rules = ("-restaurantpizza.restaurant",)

    def __repr__(self):
        return f"<Restaurant {self.name}>"


# Pizza Model
class Pizza(db.Model, SerializerMixin):
    __tablename__ = "pizzas"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)

    # Relationships
    restaurantpizza = db.relationship(
        "RestaurantPizza",
        back_populates="pizza",
        cascade="all, delete-orphan"  # Cascade deletes
    )

    # Serialization rules
    serialize_rules = ("-restaurantpizza.pizza",)

    def __repr__(self):
        return f"<Pizza {self.name}, {self.ingredients}>"


# RestaurantPizza Model
class RestaurantPizza(db.Model, SerializerMixin):
    __tablename__ = "restaurant_pizzas"

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)

    # Foreign Keys
    pizza_id = db.Column(db.Integer, db.ForeignKey("pizzas.id"), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)

    # Relationships
    restaurant = db.relationship("Restaurant", back_populates="restaurantpizza")
    pizza = db.relationship("Pizza", back_populates="restaurantpizza")

    # Serialization rules
    serialize_rules = ("-restaurant.restaurantpizza", "-pizza.restaurantpizza")

    # Validation for price
    @validates("price")
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("validation errors")
        
        # if value == 0:
        #     raise KeyError("Price must be above 0")
        
        return value


    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"
