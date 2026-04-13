from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "cindrella_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

# ---------------- DB ----------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    img = db.Column(db.String(500))
    category = db.Column(db.String(50))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        if u == "admin" and p == "1234":
            session["admin"] = True
            session["user"] = False
            return redirect("/admin")

        user = User.query.filter_by(username=u).first()
        if not user:
            user = User(username=u, password=p)
            db.session.add(user)
            db.session.commit()

        session["user"] = True
        session["username"] = u
        session["admin"] = False

        return redirect("/home")

    return render_template("login.html")

# ---------------- HOME ----------------
@app.route("/home")
def home():
    if not session.get("user") and not session.get("admin"):
        return redirect("/")
    return render_template("home.html")

# ---------------- PRODUCTS ----------------
@app.route("/products")
def products():
    return render_template("products.html", products=Product.query.all())

# ---------------- ADD TO CART ----------------
@app.route("/add/<int:id>")
def add(id):
    p = Product.query.get(id)

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append({
        "name": p.name,
        "price": p.price
    })

    session.modified = True
    return redirect("/products")

# ---------------- CART ----------------
@app.route("/cart")
def cart():
    cart = session.get("cart", [])
    total = sum(i["price"] for i in cart)
    return render_template("cart.html", cart=cart, total=total)

# ---------------- ABOUT ----------------
@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/")
    return render_template("admin.html", products=Product.query.all())

@app.route("/admin/add", methods=["POST"])
def add_product():
    file = request.files["img"]
    filename = secure_filename(file.filename)
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(path)

    p = Product(
        name=request.form["name"],
        price=int(request.form["price"]),
        category=request.form["category"],
        img="/static/uploads/" + filename
    )

    db.session.add(p)
    db.session.commit()
    return redirect("/admin")

@app.route("/admin/delete/<int:id>")
def delete(id):
    p = Product.query.get(id)
    db.session.delete(p)
    db.session.commit()
    return redirect("/admin")

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)