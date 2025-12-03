from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("bookstore.db")
    conn.row_factory = sqlite3.Row      # allows book.title, book.image, etc.
    return conn

def get_categories():
    conn = get_db_connection()
    categories = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return categories



@app.route("/")
def home():
    return render_template("index.html", categories=get_categories())

@app.route("/category")
def category():
    
    category_id = request.args.get("categoryId", type=int, default=1)

    conn = get_db_connection()
    books = conn.execute(
        "SELECT * FROM books WHERE categoryId = ? ORDER BY id",
        (category_id,)
    ).fetchall()
    conn.close()

    return render_template(
        "category.html",
        categories=get_categories(),
        selectedCategory=category_id,
        books=books
    )


@app.route("/search", methods=["POST"])
def search():
    term = request.form.get("titleSearch", "").strip()

    conn = get_db_connection()
    books = []
    if term:
        books = conn.execute(
            "SELECT * FROM books WHERE lower(title) LIKE lower(?) ORDER BY title",
            (f"%{term}%",)
        ).fetchall()
    conn.close()

    return render_template(
        "search.html",
        categories=get_categories(),
        books=books,
        term=term
    )

@app.route("/book/<int:book_id>")
def book_detail(book_id):
    conn = get_db_connection()
    book = conn.execute("""
        SELECT books.*, categories.name AS categoryName
        FROM books
        JOIN categories ON categories.id = books.categoryId
        WHERE books.id = ?
    """, (book_id,)).fetchone()
    conn.close()

    if book is None:
        return render_template(
            "error.html",
            error=f"Book with id {book_id} not found",
            categories=get_categories()
        )

    return render_template(
        "book_detail.html",
        categories=get_categories(),
        book=book
    )

@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", error=e, categories=get_categories())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
