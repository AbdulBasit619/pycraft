from storage.database import Database
from engines.engine import Engine


def run_sql():
    db = Database()
    db.create_table("users", ["id", "name", "age"])
    db.get_table("users").insert([1, "Alice", 25])
    db.get_table("users").insert([2, "Bob", 31])

    eng = Engine(db)
    # eng.execute("select name, age from users where age>=18 and name='Bob';")
    # eng.execute("SELECT name, age FROM users WHERE age >= 18 AND name = 'Bob';")
    eng.execute("SELECT name, age, salary FROM users")
    eng.execute("SELECT * FROM users")


if __name__ == "__main__":
    run_sql()
