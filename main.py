import json

from TOKEN_Botskiy import TOKEN
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from datetime import datetime
from db_code import add_recipe_in_db, get_all_recipe, get_user_recipe, get_recipe_by_title


async def add_recipe(update, context):
    await update.message.reply_text(
        """Вы хотите добавить свой рецепт? \n Отлично! \n Но делать действие сие нужно по шаблону для того чтобы удобно 
        читать его было потом. Для начала вы должны написать название Вот так: \n 
        1. 'Название вашего рецепта' \n Следом требуется указать ингредиенты таким вот образом: 
        2. 'Название вашего продукта(кол-во)[Мера измерения(можно указать шт. или г. или л.)]' в любом количестве, 
        но каждый продукт с новой строки. \n Затем требуется написать сам рецепт вот так: 
        3. 'Любой ваш рецепт, но не более 1000 символов',  \n Теперь требуется указать категорию вашего блюда вот так: 
        4. 'Вегетарианское' и/или 'Обед' и/или 'Ужин' и/или 'Десерт' или любое другое значение.\n  
        Также вы можете разместить какую-лтбо дополнительную информацию касательно вашего блюда вот так: 
        5. 'Любая информация касательно блюда' \n Если хотите отменить ввод рецепта то напишите /stop_recipe """
    )
    await update.message.reply_text(
        "Пример:\n"
        "1. Картошка_фри\n"
        "2. картофель(250)[г.]\n"
        "   растительное масло(1)[л.]\n"
        "   соль(10)[шт.]\n"
        "3. Картофель почистить и помыть.\n"
        "   Нарезать брусочками длиной 5–6 см и шириной 0,5–0,6 см.\n"
        "   Нарезанный картофель положить в миску и хорошо промыть холодной водой 2–3 раза или холодной проточной водой.\n"
        "   Откинуть на дуршлаг, выложить на бумажное полотенце и хорошо обсушить.\n"
        "   В 4-литровую кастрюлю налить растительное масло и разогреть до температуры 180–190 градусов.\n"
        "   Положить подготовленный картофель и жарить, время от времени перемешивая, до золотистого цвета.\n"
        "   Готовый картофель фри выложить на бумажное полотенце, чтобы впитался лишний жир.\n"
        "   Слегка присаливать и подавать к столу\n"
        "4. Перекус\n"
        "5. Домашняя готовка полезна для здоровья!"
    )
    return range(1)


async def process_recipe(update, context):
    recipe_text = update.message.text
    lines = recipe_text.split("\n")
    if len(lines) < 5:
        await update.message.reply_text(
            "Рецепт написан некорректно. Пожалуйста, используйте указанный шаблон."
        )
        return range(1)
    try:
        title = lines[0].split(". ", 1)[1].strip()

        ingredients_list = []
        for line in lines[1:]:
            if line.startswith("2."):
                parts = line.split(". ", 1)
                if len(parts) > 1:
                    ingredient = parts[1].strip()
                    ingredients_list.append(ingredient)

        recipe_content_lines = []
        for line in lines[1:]:
            if line.startswith("3."):
                parts = line.split(". ", 1)
                if len(parts) > 1:
                    recipe_content_lines.append(parts[1].strip())
        recipe_content = "\n".join(recipe_content_lines)

        category = "Категория отсутствует"
        if len(lines) > 3:
            if lines[3].startswith("4."):
                parts = lines[3].split(". ", 1)
                if len(parts) > 1:
                    category = parts[1].strip()

        additional_info = ""
        if len(lines) > 4:
            if lines[4].startswith("5."):
                parts = lines[4].split(". ", 1)
                if len(parts) > 1:
                    additional_info = parts[1].strip()

        recipe_data = {
            "2": title,
            "3": update.message.from_user.username or "Неизвестный пользователь",
            "4": ingredients_list,
            "5": 0,
            "6": recipe_content,
            "7": category,
            "8": datetime.now().isoformat(),
            "9": additional_info,
        }

        recipe_data["5"] = know_calories(recipe_data["4"])

        result = add_recipe_in_db(recipe_data)

        if isinstance(result, str):
            await update.message.reply_text(
                f"Произошла ошибка при добавлении рецепта в базу данных: {result}"
            )

        else:

            await update.message.reply_text(
                "Рецепт успешно получен и обработан!\n"
                f"Название: {recipe_data['2']}\n"
                f"Автор: @{recipe_data['3']}\n"
                f"Ингредиенты: {recipe_data['4']}\n"
                f"Рецепт: {recipe_data['6']}\n"
                f"Категория: {recipe_data['7']}\n"
                f"Дополнительная информация: {recipe_data['9']}"
            )

        return ConversationHandler.END
    except IndexError:
        await update.message.reply_text(
            "Неправильный формат ввода. Убедитесь, что каждый пункт начинается с номера и точки (1., 2., 3., 4., 5.)."
        )
        return range(1)


async def stop_recipe(update, context):
    await update.message.reply_text("Ввод рецепта отменен.")
    return ConversationHandler.END


async def show_all_recipes(update, context):
    recipes = get_all_recipe()
    if recipes:
        message = "Все рецепты:\n"
        for recipe_id, title in recipes:
            message += f"{recipe_id}. {title}\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Рецепты нечитаемы")


async def show_my_recipes(update, context):
    username = update.message.from_user.username

    recipes = get_user_recipe(username)
    if recipes:
        message = f"Ваши рецепты (@{username}):\n"
        for recipe_id, title in recipes:
            message += f"{recipe_id}. {title}\n"
        await update.message.reply_text(message)
    else:
        await update.message.reply_text(f"Вы не добавили ни одного рецепта (@{username}).")


async def show_recipe(update, context):
    try:
        title = context.args[0]
    except IndexError:
        await update.message.reply_text("Пожалуйста, укажите название рецепта после команды /recipe "
                                        "(например, /recipe Картофельные чипсы)")
        return

    recipe = get_recipe_by_title(title)
    if recipe:
        message = (

                f"1. {recipe['title']}\n"
                f"2. " + "\n   ".join(recipe['ingredients']) + "\n"
                                                               f"3. {recipe['recipe_text']}\n"
                                                               f"4. {recipe['category']}\n"
                                                               f"5. {recipe['additional_info']}\n"
                                                               f"6. Добавлено пользователем @{recipe['author']}\n"
                                                               f"7. Калории: {recipe['calories']} ккал\n"
                                                               f"8. Вероятная цена: {know_price(recipe['ingredients'])} руб."
        )

        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Рецепт не найден.")


def know_calories(ingredients_list):
    all_calories = 0.0
    with open("calories.json", "r", encoding="utf-8") as f:
        calories_data = json.load(f)

    for ingredient_str in ingredients_list:
        try:
            name_kolvo, unit_part = ingredient_str.split("[")
            unit = unit_part.replace("]", "")

            name, kolvo_str = name_kolvo.split("(")
            kolvo_str = kolvo_str.replace(")", "")
            ingredient_name = name.strip().lower()
            quantity = float(kolvo_str)
        except ValueError:
            print(f"Не удалось разобрать формат ингредиента '{ingredient_str}'.")
            continue
        except IndexError:
            print(f"Неправильный формат ингредиента '{ingredient_str}'.")
            continue

        if ingredient_name in calories_data:
            calories_per_100g = calories_data[ingredient_name]["калории"]

            if unit == "г" or unit == "г.":
                calories = (quantity / 100) * calories_per_100g
            elif unit == "кг" or unit == "кг.":
                calories = (quantity * 1000 / 100) * calories_per_100g
            elif unit == "шт" or unit == "шт.":
                calories = quantity * (calories_per_100g / 100 * 100)
            elif unit == "мл" or unit == "мл.":
                calories = (quantity / 100) * calories_per_100g
            elif unit == "л" or unit == "л.":
                calories = (quantity * 1000 / 100) * calories_per_100g
            else:
                print(f"Неизвестная единица измерения '{unit}' для '{ingredient_name}'. Использую калории на 100 г.")
                calories = (quantity / 100) * calories_per_100g

            all_calories += calories
        else:
            print(f"Данные о калорийности для '{ingredient_name}' не найдены.")

    return all_calories


async def start_command(update, context):
    message = (
        "Привет! Я кулинарный бот-помощник.\n"
        "Я помогу тебе добавлять, искать и обмениваться рецептами, "
        "а также подсчитывать калорийность и примерную стоимость блюд.\n\n"
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/add_recipe - Добавить новый рецепт\n"
        "/show_all_recipes - Показать все рецепты\n"
        "/show_my_recipes - Показать мои рецепты\n"
        "/recipe <название_рецепта> - Показать рецепт по названию\n"
        "/stop_recipe - Остановить ввод рецепта"
    )
    await update.message.reply_text(message)


async def help_command(update, context):
    message = (
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/add_recipe - Добавить новый рецепт\n"
        "/show_all_recipes - Показать все рецепты\n"
        "/show_my_recipes - Показать мои рецепты\n"
        "/recipe <название_рецепта> - Показать рецепт по названию\n"
        "/stop_recipe - Остановить ввод рецепта"
    )
    await update.message.reply_text(message)


def know_price(ingredients_list):
    return 100


if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    add_recipe_handler = ConversationHandler(
        entry_points=[CommandHandler("add_recipe", add_recipe)],
        states={range(1): [MessageHandler(filters.TEXT & ~filters.COMMAND, process_recipe)]},
        fallbacks=[CommandHandler("stop_recipe", stop_recipe)],
    )
    application.add_handler(add_recipe_handler)
    application.add_handler(CommandHandler("show_all_recipes", show_all_recipes))
    application.add_handler(CommandHandler("show_my_recipes", show_my_recipes))
    application.add_handler(CommandHandler("recipe", show_recipe))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.run_polling()
