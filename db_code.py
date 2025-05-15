import sqlite3
import json


def add_recipe_in_db(recipe_data, db_name='recipes.sqlite'):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        title = recipe_data["2"]
        author = recipe_data["3"]
        ingredients = recipe_data["4"]
        calories = recipe_data["5"] or 0
        recipe_text = recipe_data["6"]
        category = recipe_data["7"]
        time = recipe_data["8"]
        additional_info = recipe_data["9"]

        ingredients_json = json.dumps(ingredients)

        cursor.execute("""
            INSERT INTO recipes (title, author, ingredients_json, calories, recipe_text, category, time, additional_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, author, ingredients_json, calories, recipe_text, category, time, additional_info))

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"ошибка: {e}")
        return str(e)


    finally:
        conn.close()


def get_all_recipe(db_name='recipes.sqlite'):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title FROM recipes ORDER BY id")
        recipes = cursor.fetchall()
        return recipes

    except sqlite3.Error as e:
        print(f"ошибка {e}")
        return [f"ошибка {e}"]

    finally:
        conn.close()


def get_user_recipe(author, db_name='recipes.sqlite'):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        cursor.execute("SELECT id, title FROM recipes WHERE author = ? ORDER BY id", (author,))
        recipes = cursor.fetchall()
        return recipes

    except sqlite3.Error as e:
        print(f"ошибка {e}")
        return [f"ошибка {e}"]

    finally:
        conn.close()


def get_recipe_by_title(title, db_name='recipes.sqlite'):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recipes WHERE title = ?", (title,))
        recipe = cursor.fetchone()
        if recipe:
            recipe_dict = {
                "id": recipe[0],
                "title": recipe[1],
                "author": recipe[2],
                "ingredients": json.loads(recipe[3]),
                "calories": recipe[4],
                "recipe_text": recipe[5],
                "category": recipe[6],
                "time": recipe[7],
                "additional_info": recipe[8]
            }
            return recipe_dict
        else:
            return None

    except sqlite3.Error as e:
        print(f"ошибка {e}")
        return None

    finally:
        conn.close()
