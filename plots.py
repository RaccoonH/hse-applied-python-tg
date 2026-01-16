import matplotlib.pyplot as plt
from matplotlib.patches import Patch


def draw_hbar(items, user_id):
    fig, ax = plt.subplots(2, 1)
    count = 0
    for name, values in items.items():
        ax[count].barh(name, values[0], height=0.5, color='#b5ffb9', label="Потреблено")
        diff = values[1] - values[0]
        if diff > 0:
            ax[count].barh(name, diff, left=values[0], height=0.5, color='#f9bc86', label="Осталось до нормы")
        elif diff < 0:
            ax[count].barh(name, -1 * diff, left=values[1], height=0.5, color="#f84e4e", label="Потреблено сверх нормы")
        count += 1

    png_file = f"/tmp/{user_id}_tmp.png"
    ax[0].set_title("Ваш прогресс")

    legend_elements = [
        Patch(facecolor='#b5ffb9', label='Потреблено'),
        Patch(facecolor='#f9bc86', label='Осталось до нормы'),
        Patch(facecolor='#f84e4e', label='Потреблено сверх нормы')
    ]

    fig.legend(handles=legend_elements, loc='lower center', ncols=3, bbox_to_anchor=(0.5, -0.05))
    plt.savefig(png_file, format="png", bbox_inches="tight")
    plt.close()

    return png_file
