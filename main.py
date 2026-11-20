import sqlite3  # Use SQLite to store expenses.
from fastapi import FastAPI, HTTPException  # Create API routes and errors.
from pydantic import BaseModel, Field  # Validate incoming data.

app = FastAPI()  # Create the application.


class Expense(BaseModel):
    description: str = Field(min_length=1)  # Require a description.
    amount: float = Field(gt=0)  # Require a positive amount.


def connect():
    db = sqlite3.connect("expenses.db")  # Open the local database.
    db.row_factory = sqlite3.Row  # Allow columns to be read by name.
    return db


with connect() as db:  # Create the table if it does not exist.
    db.execute(
        "CREATE TABLE IF NOT EXISTS expenses "
        "(id INTEGER PRIMARY KEY, description TEXT, amount REAL)"
    )


@app.post("/expenses", status_code=201)
def add_expense(expense: Expense):
    with connect() as db:
        cursor = db.execute(  # Save the expense.
            "INSERT INTO expenses (description, amount) VALUES (?, ?)",
            (expense.description, expense.amount),
        )
        return {"id": cursor.lastrowid, **expense.model_dump()}


@app.get("/expenses")
def list_expenses():
    with connect() as db:
        rows = db.execute("SELECT * FROM expenses").fetchall()
        return [dict(row) for row in rows]  # Return all saved expenses.


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    with connect() as db:
        cursor = db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        if cursor.rowcount == 0:  # Handle an unknown expense ID.
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"message": "Expense deleted"}
