from flask import Flask, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates')

# Caminho do banco de dados
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELO ATUALIZADO
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    complete = db.Column(db.Boolean, default=False)
    date_time = db.Column(db.DateTime, default=datetime.utcnow)  # NOVO
    notes = db.Column(db.Text)  # NOVO

with app.app_context():
    db.create_all()

# ROTA PRINCIPAL COM FILTRO
@app.route('/')
def home():
    filter_type = request.args.get("filter", "all")
    if filter_type == "incomplete":
        todo_list = Todo.query.filter_by(complete=False).order_by(Todo.date_time).all()
    else:
        todo_list = Todo.query.order_by(Todo.date_time).all()
    return render_template("base.html", todo_list=todo_list, filter_type=filter_type)

# ADICIONAR NOVA TAREFA
@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    notes = request.form.get("notes")
    date_str = request.form.get("date_time")
    date_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M") if date_str else datetime.utcnow()

    new_todo = Todo(title=title, notes=notes, date_time=date_time, complete=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("home"))

# ATUALIZAR STATUS
@app.route("/update/<int:todo_id>")
def update(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("home"))

# DELETAR
@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("home"))

# EDITAR TAREFA
@app.route("/edit/<int:todo_id>", methods=["GET", "POST"])
def edit(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == "POST":
        todo.title = request.form.get("title")
        todo.notes = request.form.get("notes")
        date_str = request.form.get("date_time")
        todo.date_time = datetime.strptime(date_str, "%Y-%m-%dT%H:%M") if date_str else todo.date_time
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", todo=todo)

def create_app():
    with app.app_context():
        db.create_all()
    return app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)