from datetime import datetime, timezone, timedelta
import data.workouts as workouts

users = dict()


class UserDailyInfo:
    def __init__(self, timezone_hour, weight, sport_time, is_male, height, age):
        self.water_curr = 0
        self.water_goal = weight * 30 + (500 * (sport_time // 30))
        if not is_male:
            self.water_goal *= 0.9
        self.water_goal = round(self.water_goal)

        self.calories_burned = 0
        self.calories_eaten = 0
        if is_male:
            self.calories_goal = 66.5 + (13.75 * weight) + (5.003 * height) - (6.775 * age)
        else:
            self.calories_goal = 655.1 + (9.563 * weight) + (1.85 * height) - (4.676 * age)
        self.today_date = datetime.now(timezone.utc) + timedelta(hours=timezone_hour)


class UserInfo:
    def __init__(self, user_id, name, age, weight, height, is_male, sport_time, city, timezone):
        self.id = user_id
        self.name = name
        self.age = age
        self.weight = weight
        self.height = height
        self.is_male = is_male
        self.sport_time = sport_time
        self.city = city
        self.timezone = timezone

        self.daily = UserDailyInfo(timezone, weight, sport_time, is_male, height, age)

    def update_daily_info(self, force):
        cur_date = datetime.now(timezone.utc) + timedelta(hours=self.timezone)
        if (cur_date.date() != self.daily.today_date.date()) or force:
            self.daily = UserDailyInfo(timezone, self.weight, self.sport_time, self.is_male, self.height, self.age)


def find_user(user_id):
    return user_id in users


def add_user(user_id, name, age, weight, height, is_male, sport_time, city, timezone):
    users[user_id] = UserInfo(user_id, name, age, weight, height, is_male, sport_time, city, timezone)


def remove_user(user_id):
    if user_id in users:
        del users[user_id]


def get_user(user_id):
    return users[user_id]


def update_user_daily_info(user_id, force=False):
    user = get_user(user_id)
    user.update_daily_info(force)


def log_water(user_id, water_number):
    users[user_id].daily.water_curr += water_number
    return users[user_id].daily.water_curr


def get_water_goal(user_id):
    user = get_user(user_id)
    return user.daily.water_goal


def get_calories_goal(user_id):
    user = get_user(user_id)
    return user.daily.calories_goal


def log_workout(user_id, workout, duration):
    user = get_user(user_id)
    calories_burned = workouts.calculate_calories(user_id, workout, user.weight, duration)
    user.daily.calories_burned += calories_burned
    return calories_burned


def log_food(user_id, calories):
    user = get_user(user_id)
    user.daily.calories_eaten += calories
    return user.daily.calories_eaten


class UserProgress:
    water_curr: int
    water_intake: int
    calories_burned: float
    calories_eaten: float
    calories_standard: float


def get_progress(user_id):
    user = get_user(user_id)

    progress = UserProgress()
    progress.water_curr = user.daily.water_curr
    progress.water_intake = user.daily.water_goal
    progress.calories_burned = user.daily.calories_burned
    progress.calories_eaten = user.daily.calories_eaten
    progress.calories_standard = user.daily.calories_goal

    return progress
