from storage.database import Database
from engines.engine import Engine


def run_sql():
    db = Database()
    db.create_table("users", ["id", "name", "age"])
    db.get_table("users").insert([1, "Alice", 25])
    db.get_table("users").insert([2, "Bob", 31])

    eng = Engine(db)
    eng.execute(
        "SELECT name, age FROM users WHERE name = 'Bob' AND NOT (id = 2 OR age >= 30) ORDER BY name DESC, age ASC;"
    )
    eng.execute("CREATE TABLE users (id, name, age);")


if __name__ == "__main__":
    run_sql()
