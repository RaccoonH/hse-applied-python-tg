import pandas as pd

df = pd.read_csv("data/russian_items.csv", index_col=0)
user_foods = dict()


def find_food(user_id, food_name):
    df_user_food = user_foods.setdefault(user_id, df.iloc[:0].copy())
    df_food = pd.concat([df, df_user_food], ignore_index=True)
    result = df_food[df_food['product_name'].str.contains(food_name, case=False)]
    return result


def get_food_by_id(user_id, food_id):
    df_user_food = user_foods.setdefault(user_id, df.iloc[:0].copy())
    df_food = pd.concat([df, df_user_food], ignore_index=True)
    return df_food.loc[food_id]


def add_user_food(user_id, food_name, calories):
    df_user_food = user_foods.setdefault(user_id, df.iloc[:0].copy())
    df_user_food.loc[len(df_user_food)] = [food_name, calories]
