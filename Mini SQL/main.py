from storage.database import Database
from engines.engine import Engine


def run_sql():
    db = Database()
    db.create_table("users", ["id", "name", "age"])
    db.get_table("users").insert([1, "Alice", 25])
    db.get_table("users").insert([2, "Bob", 31])

    eng = Engine(db)
    # eng.execute(
    #     "SELECT name, age FROM users WHERE name = 'Bob' AND NOT (id = 2 OR age >= 30) ORDER BY name DESC, age ASC;"
    # )
    # eng.execute("CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(30), age INT);")
    # eng.execute(
    #     "INSERT INTO users (id, name, age) VALUES (1, 'Alice', 25), (2, 'Bob', 31);"
    # )
    # eng.execute("UPDATE users SET age = 30, name = 'Peter' WHERE age >= 20;")
    eng.execute("DELETE FROM users WHERE name = 'Bob' OR (age < 20 AND NOT id = 3);")


if __name__ == "__main__":
    run_sql()
