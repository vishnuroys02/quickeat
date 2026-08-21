import os
from datetime import datetime, timezone
from functools import wraps
import jwt
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app=Flask(__name__)
app.config["SECRET_KEY"]=os.getenv("SECRET_KEY","dev-secret")
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("DATABASE_URL","sqlite:///quickeats.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)
CORS(app,origins=os.getenv("CORS_ORIGINS","*"))

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(150),unique=True,nullable=False); password_hash=db.Column(db.String(255),nullable=False)
    role=db.Column(db.String(20),default="customer",nullable=False); created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))

class Food(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),nullable=False)
    category=db.Column(db.String(80),nullable=False); description=db.Column(db.String(300),default="")
    price=db.Column(db.Float,nullable=False); image=db.Column(db.String(500),default=""); available=db.Column(db.Boolean,default=True)

class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    total_amount=db.Column(db.Float,nullable=False); status=db.Column(db.String(30),default="Pending",nullable=False)
    created_at=db.Column(db.DateTime,default=lambda:datetime.now(timezone.utc))

class OrderItem(db.Model):
    id=db.Column(db.Integer,primary_key=True); order_id=db.Column(db.Integer,db.ForeignKey("order.id"),nullable=False)
    food_id=db.Column(db.Integer,db.ForeignKey("food.id"),nullable=False); quantity=db.Column(db.Integer,nullable=False); price=db.Column(db.Float,nullable=False)

def current_user():
    a=request.headers.get("Authorization","")
    if not a.startswith("Bearer "): return None
    try:
        p=jwt.decode(a.split(" ",1)[1],app.config["SECRET_KEY"],algorithms=["HS256"])
        return db.session.get(User,p["user_id"])
    except (jwt.InvalidTokenError,KeyError): return None

def auth(admin=False):
    def deco(fn):
        @wraps(fn)
        def w(*args,**kwargs):
            u=current_user()
            if not u:return jsonify({"error":"Authentication required"}),401
            if admin and u.role!="admin":return jsonify({"error":"Admin access required"}),403
            return fn(u,*args,**kwargs)
        return w
    return deco

def ud(u):return {"id":u.id,"name":u.name,"email":u.email,"role":u.role}
def fd(f):return {"id":f.id,"name":f.name,"category":f.category,"description":f.description,"price":f.price,"available":f.available}

@app.get("/health")
def health():return jsonify({"status":"healthy","service":"quickeats-backend"})

@app.post("/api/auth/register")
def register():
    d=request.get_json() or {}; name=d.get("name","").strip(); email=d.get("email","").strip().lower(); pw=d.get("password","")
    if not name or not email or len(pw)<6:return jsonify({"error":"Name, valid email and password 6+ characters are required"}),400
    if User.query.filter_by(email=email).first():return jsonify({"error":"Email already registered"}),409
    u=User(name=name,email=email,password_hash=generate_password_hash(pw));db.session.add(u);db.session.commit()
    return jsonify({"message":"Registration successful","user":ud(u)}),201

@app.post("/api/auth/login")
def login():
    d=request.get_json() or {};u=User.query.filter_by(email=d.get("email","").strip().lower()).first()
    if not u or not check_password_hash(u.password_hash,d.get("password","")):return jsonify({"error":"Invalid email or password"}),401
    token=jwt.encode({"user_id":u.id,"exp":int(datetime.now(timezone.utc).timestamp())+86400},app.config["SECRET_KEY"],algorithm="HS256")
    return jsonify({"token":token,"user":ud(u)})

@app.get("/api/foods")
def foods():return jsonify([fd(f) for f in Food.query.order_by(Food.id.desc()).all()])

@app.post("/api/foods")
@auth(admin=True)
def create_food(u):
    d=request.get_json() or {}
    try:
        f=Food(name=d["name"],category=d["category"],description=d.get("description",""),price=float(d["price"]))
        db.session.add(f);db.session.commit();return jsonify(fd(f)),201
    except (KeyError,TypeError,ValueError):db.session.rollback();return jsonify({"error":"Invalid food data"}),400

@app.put("/api/foods/<int:food_id>")
@auth(admin=True)
def update_food(u,food_id):
    f=db.session.get(Food,food_id)
    if not f:return jsonify({"error":"Food not found"}),404
    d=request.get_json() or {};f.name=d.get("name",f.name);f.category=d.get("category",f.category);f.description=d.get("description",f.description)
    if "price" in d:f.price=float(d["price"])
    f.available=bool(d.get("available",f.available));db.session.commit();return jsonify(fd(f))

@app.delete("/api/foods/<int:food_id>")
@auth(admin=True)
def delete_food(u,food_id):
    f=db.session.get(Food,food_id)
    if not f:return jsonify({"error":"Food not found"}),404
    db.session.delete(f);db.session.commit();return jsonify({"message":"Food deleted"})

@app.post("/api/orders")
@auth()
def create_order(u):
    items=(request.get_json() or {}).get("items",[])
    if not items:return jsonify({"error":"Cart is empty"}),400
    total=0;valid=[]
    for x in items:
        f=db.session.get(Food,int(x["food_id"]));q=int(x.get("quantity",1))
        if not f or not f.available or q<1:return jsonify({"error":"Invalid food item or quantity"}),400
        total+=f.price*q;valid.append((f,q))
    o=Order(user_id=u.id,total_amount=round(total,2));db.session.add(o);db.session.flush()
    for f,q in valid:db.session.add(OrderItem(order_id=o.id,food_id=f.id,quantity=q,price=f.price))
    db.session.commit();return jsonify({"message":"Order placed","order_id":o.id,"total":o.total_amount}),201

@app.get("/api/orders")
@auth()
def orders(u):
    out=[]
    for o in Order.query.filter_by(user_id=u.id).order_by(Order.id.desc()).all():
        out.append({"id":o.id,"total_amount":o.total_amount,"status":o.status,"created_at":o.created_at.isoformat(),
        "items":[{"food_id":i.food_id,"quantity":i.quantity,"price":i.price} for i in OrderItem.query.filter_by(order_id=o.id).all()]})
    return jsonify(out)

@app.delete("/api/orders/<int:order_id>")
@auth()
def cancel(u,order_id):
    o=db.session.get(Order,order_id)
    if not o or o.user_id!=u.id:return jsonify({"error":"Order not found"}),404
    if o.status not in ("Pending","Confirmed"):return jsonify({"error":"Order cannot be cancelled"}),400
    o.status="Cancelled";db.session.commit();return jsonify({"message":"Order cancelled"})

@app.get("/api/admin/orders")
@auth(admin=True)
def admin_orders(u):
    out=[]
    for o in Order.query.order_by(Order.id.desc()).all():
        c=db.session.get(User,o.user_id);out.append({"id":o.id,"customer":c.name if c else "Unknown","email":c.email if c else "",
        "total_amount":o.total_amount,"status":o.status,"created_at":o.created_at.isoformat()})
    return jsonify(out)

@app.put("/api/orders/<int:order_id>/status")
@auth(admin=True)
def status(u,order_id):
    o=db.session.get(Order,order_id)
    if not o:return jsonify({"error":"Order not found"}),404
    s=(request.get_json() or {}).get("status");allowed={"Pending","Confirmed","Preparing","Out for Delivery","Delivered","Cancelled"}
    if s not in allowed:return jsonify({"error":"Invalid status"}),400
    o.status=s;db.session.commit();return jsonify({"message":"Order status updated","status":s})

@app.get("/api/admin/users")
@auth(admin=True)
def admin_users(u):return jsonify([ud(x) for x in User.query.order_by(User.id.desc()).all()])

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@quickeats.local").first():
        db.session.add(User(name="QuickEats Admin",email="admin@quickeats.local",password_hash=generate_password_hash("admin123"),role="admin"))
    if Food.query.count()==0:
        db.session.add_all([Food(name="Chicken Biryani",category="Biryani",description="Aromatic basmati rice with chicken.",price=180),
        Food(name="Paneer Butter Masala",category="North Indian",description="Creamy tomato gravy with paneer.",price=160),
        Food(name="Veg Burger",category="Burgers",description="Crispy veggie patty.",price=120),
        Food(name="Chicken Pizza",category="Pizza",description="Cheesy pizza with chicken.",price=250),
        Food(name="Masala Dosa",category="South Indian",description="Crispy dosa with potato masala.",price=90)])
    db.session.commit()

if __name__=="__main__":app.run(host="0.0.0.0",port=5000)
