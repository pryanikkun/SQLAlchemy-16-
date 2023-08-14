from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from data import users, orders, offers

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_AS_ASCII"] = False

app.app_context().push()
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    age = db.Column(db.Integer)
    email = db.Column(db.String(50))
    role = db.Column(db.String(50))
    phone = db.Column(db.String(50))


class Offer(db.Model):
    __tablename__ = "offer"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(500))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(50))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    executor_id = db.Column(db.Integer, db.ForeignKey("user.id"))


db.drop_all()
db.create_all()


def insert_data():
    new_users = []
    for user in users:
        new_users.append(User(
            id=user['id'],
            first_name=user["first_name"],
            last_name=user["last_name"],
            age=user["age"],
            email=user["email"],
            role=user["role"],
            phone=user["phone"]
        ))

    with db.session.begin():
        db.session.add_all(new_users)

    new_orders = []
    for order in orders:
        new_orders.append(Order(
            id=order['id'],
            name=order["name"],
            start_date=datetime.strptime(order["start_date"], '%m/%d/%Y'),
            end_date=datetime.strptime(order["end_date"], '%m/%d/%Y'),
            description=order["description"],
            address=order["address"],
            price=order["price"],
            customer_id=order["customer_id"],
            executor_id=order["executor_id"]
        ))

    with db.session.begin():
        db.session.add_all(new_orders)

    new_offers = []
    for offer in offers:
        new_offers.append(Offer(
            id=offer['id'],
            order_id=offer["order_id"],
            executor_id=offer["executor_id"]
        ))

    with db.session.begin():
        db.session.add_all(new_offers)


insert_data()


@app.route('/users')
def get_users():
    """
    Выводит всех пользователей в JSON формате
    """
    users_list = User.query.all()
    users_response = []

    for user in users_list:
        users_response.append({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "age": user.age,
            "email": user.email,
            "role": user.role,
            "phone": user.phone
        })

    return jsonify(users_response)


@app.route('/users', methods=["POST"])
def add_users():
    """
    Позволяет добавить нового пользователя
    """
    request_data = request.get_json()
    new_user = User(
        id=request_data["id"],
        first_name=request_data["first_name"],
        last_name=request_data["last_name"],
        age=request_data["age"],
        email=request_data["email"],
        role=request_data["role"],
        phone=request_data["phone"]
    )

    with db.session.begin():
        db.session.add(new_user)

    return '', 201


@app.route('/users/<int:uid>')
def get_user_by_id(uid):
    user = User.query.get(uid)

    if user is None:
        return "not found"

    user_response = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "age": user.age,
        "email": user.email,
        "role": user.role,
        "phone": user.phone
    }

    return jsonify(user_response)


@app.route('/users/<int:uid>', methods=["PUT"])
def update_new_user(uid):
    request_data = request.get_json()
    user = User.query.get(uid)

    if user is None:
        return "not found"

    user.id = request_data["id"]
    user.first_name = request_data["first_name"]
    user.last_name = request_data["last_name"]
    user.age = request_data["age"]
    user.email = request_data["email"]
    user.role = request_data["role"]
    user.phone = request_data["phone"]

    db.session.add(user)
    db.session.commit()

    return '', 201


@app.route('/users/<int:uid>', methods=["DELETE"])
def delete_user(uid):
    user = User.query.get(uid)

    if user is None:
        return "not found"

    db.session.delete(user)
    db.session.commit()

    return '', 201


@app.route('/orders', methods=["GET", "POST"])
def get_orders():
    if request.method == "GET":
        orders_list = Order.query.all()
        orders_response = []

        for order in orders_list:
            customer = User.query.get(order.customer_id).first_name if User.query.get(
                order.customer_id) else order.customer_id
            executor = User.query.get(order.executor_id).first_name if User.query.get(
                order.executor_id) else order.executor_id
            orders_response.append({
                "id": order.id,
                "name": order.name,
                "description": order.description,
                "start_date": order.start_date,
                "end_date": order.end_date,
                "address": order.address,
                "price": order.price,
                "customer_id": customer,
                "executor_id": executor
            })
        return jsonify(orders_response)

    elif request.method == "POST":
        # Тут нужен postman.
        # Там в Body вводятся данные в формате JSON и вот мы их получаем
        request_data = request.get_json()
        new_order = Order(
            name=request_data["name"],
            start_date=datetime.strptime(request_data["start_date"], '%m/%d/%Y'),
            end_date=datetime.strptime(request_data["end_date"], '%m/%d/%Y'),
            description=request_data["description"],
            address=request_data["address"],
            price=request_data["price"],
            customer_id=request_data["customer_id"],
            executor_id=request_data["executor_id"]
        )

        with db.session.begin():
            db.session.add(new_order)

        return '', 201


@app.route('/orders/<int:uid>', methods=["GET", "PUT", "DELETE"])
def get_order_by_id(uid):
    if request.method == "GET":
        order = Order.query.get(uid)

        if order is None:
            return "not found"

        return jsonify({
            "id": order.id,
            "name": order.name,
            "description": order.description,
            "start_date": order.start_date,
            "end_date": order.end_date,
            "address": order.address,
            "price": order.price,
            "customer_id": order.customer_id,
            "executor_id": order.executor_id
        })
    elif request.method == "PUT":
        # тут тоже просто меняется через postman
        request_data = request.get_json()
        order = Order.query.get(uid)

        if order is None:
            return "not found"

        order.name = request_data["name"]
        order.start_date = datetime.strptime(request_data["start_date"], '%m/%d/%Y')
        order.end_date = datetime.strptime(request_data["end_date"], '%m/%d/%Y')
        order.description = request_data["description"]
        order.address = request_data["address"]
        order.price = request_data["price"]
        order.customer_id = request_data["customer_id"]
        order.executor_id = request_data["executor_id"]

        db.session.add(order)
        db.session.commit()

        return '', 201

    elif request.method == "DELETE":
        order = Order.query.get(uid)

        db.session.delete(order)
        db.session.commit()

        return '', 201


@app.route('/offers')
def get_offers():
    offers_list = Offer.query.all()
    offers_response = []

    for offer in offers_list:
        offers_response.append({
            "id": offer.id,
            "order_id": offer.order_id,
            "executor_id": offer.executor_id
        })

    return jsonify(offers_response)


@app.route('/offers', methods=["POST"])
def add_offer():
    request_data = request.get_json()
    new_offer = Offer(
        id=request_data["id"],  # тут наверное можно убрать id, чтобы оно заполнялось автоматически
        order_id=request_data["order_id"],
        executor_id=request_data["executor_id"]
    )

    db.session.add(new_offer)
    db.session.commit()

    return '', 201


@app.route('/offers/<int:uid>')
def get_offer_by_id(uid):
    offer = Offer.query.get(uid)

    if offer is None:
        return "not found"

    return jsonify({
        "id": offer.id,
        "order_id": offer.order_id,
        "executor_id": offer.executor_id
    })


@app.route('/offers/<int:uid>', methods=["PUT"])
def update_offer_by_id(uid):
    offer = Offer.query.get(uid)

    if offer is None:
        return "not found"

    request_data = request.get_json()

    offer.order_id = request_data["order_id"]
    offer.executor_id = request_data["executor_id"]

    db.session.add(offer)
    db.session.commit()

    return '', 201


@app.route('/offers/<int:uid>', methods=["DELETE"])
def delete_offer_by_id(uid):
    offer = Offer.query.get(uid)

    if offer is None:
        return "not found"

    db.session.delete(offer)
    db.session.commit()

    return '', 201


if __name__ == "__main__":
    # app.run(debug=True, use_reloader=False)
    app.run()
