workouts_met = {
    "ходьба": 3.5,
    "бег": 8.3,
    "силовая тренировка": 6,
    "кроссфит": 8.5,
    "велотренажёр": 7,
    "плавание": 7
}
user_workouts = dict()


def is_workout_available(user_id, workout):
    workouts = get_available_workouts(user_id)
    return workout.lower() in workouts


def calculate_calories(user_id, workout, weight, duration):
    workouts = get_available_workouts(user_id)
    return int(workouts[workout.lower()] * weight * (duration / 60))


def add_workout(user_id, workout, met):
    user_workouts.setdefault(user_id, dict())[workout] = met


def get_available_workouts(user_id):
    user_workouts.setdefault(user_id, dict())
    return workouts_met | user_workouts[user_id]
