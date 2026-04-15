import os
import sqlite3
from fastmcp import FastMCP

"Create an instance for FastMCP"
mcp = FastMCP(name="Expense Tracker")

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")
Categories_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

def db_init():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
                  CREATE TABLE IF NOT EXISTS expenses(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT ''
                  )
                """)
db_init()


@mcp.tool
def add_expense(amount, date, category,subcategory="", note=""):
    """Add an expense to the database."""
    with sqlite3.connect(DB_PATH) as c:
        conn= c.execute("""
                  INSERT INTO expenses (amount, date, category, subcategory, note), values (?, ?, ?, ?, ?),
                    """,
                  (amount,date,category,subcategory,note)
                  )
    return{"status": "ok", "id" : conn.lastrowid}

@mcp.tool
def list_expenses(start_date, end_date):
    """List the expenses between the given dates."""
    with sqlite3.connect(DB_PATH) as c:
          conn=  c.execute("""
                      SELECT id, amount, date, category, subcategory, note 
                      From expenses
                      WHERE date Between ? and ?
                      Order BY date ASC                     
                      """,
                    (start_date, end_date)
            )
    column= [d[0] for d in conn.description]
    return [dict(zip(column,row)) for row in conn.fetchall()]

@mcp.tool
def delete_expense(id):
    """Delete an expense from the db"""
    with sqlite3.connect(DB_PATH) as c:
           conn=  c.execute("""
                      DELETE FROM expenses
                      WHERE id=?
                      """,
                      (id,)
                    )
    return {"status" : "ok", "deleted_rows": conn.rowcount}

@mcp.tool
def summarize_expense(start_date,end_date,category=None):
    """Summarize the expenses between the given dates, optionally filtered by category."""
    with sqlite3.connect(DB_PATH) as c:
        query= (
        """
        SELECT category, SUM(amount) as total_amount
        FROM expenses
        WHERE date between ? and ?
        """
        )
        params = [start_date, end_date]
        if category:
            query= query+ "AND category=?"
            params.append(category)

        query = query+ "GROUP BY catogory ORDER BY category ASC"
        conn= c.execute(query, params)
        column= [d[0]for d in conn.description]
        return [dict(zip(column,row))for row in conn.fetchall()]
    
    @mcp.tool
    def expense_update(id, amount=None, date=None, cateogory=None,subcategory=None,note=None):
        """Update an expense in the database."""
        with sqlite3.connect(DB_PATH) as c:
            feilds = []
            params = []
            if amount is not None:
                feilds.append("amount = ?")
                params.append(amount)
            if date is not None:
                feilds.append("date =?")
                params.append(date)
            if cateogory is not None:
                feilds.append("category = ?")
                params.append(category)
            if subcategory is not None: 
                feilds.append("subcateogory = ?")
                params.append(subcategory)
            if note is not None:
                feilds.append("note = ?")
                params.append(note)

            if not feilds:
                return {"status": "ok", "message": "No fields to update."}
            query=f"""
            Udpate expenses
            Set {",".join(feilds)}
            Where id =
            """
            params.append(id)

            curr= c.execute(params,feilds)
            return {"status": "ok", "updated_rows": curr.rowcount, "id": id}
        
    @mcp.resource("Expense://categories", mime_type="application/json")
    def categories():
        with open(Categories_PATH, "r", encoding="utf-8") as f:
            return f.read()

     
if __name__ == "__main__":
    mcp.run()