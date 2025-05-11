import gradio as gr
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
import joblib
import warnings
from data_base import SavesDataUsers, SavesDataStudents

warnings.filterwarnings("ignore")

# Загрузка данных и модели
df = pd.read_csv('D:\\УЧЕБА_УРФУ\\Программирование\\4_семестр\\Проект\\dlya_modeli.csv')
model = joblib.load('D:\\УЧЕБА_УРФУ\\Программирование\\4_семестр\\Проект\\model_1.pkl')

subjects = [
    "Вероятность и статистика", "Геометрия", "Обществознание",
    "Русский язык", "Современная литература", "Труд",
    "Физ-ра", "Физика", "Химия"
]

def get_student_class_data(student_id, class_num):
    """Возвращает данные ученика для указанного класса."""
    student_data = df[(df['Student'] == student_id) & (df['Class'] == class_num)]
    if student_data.empty:
        raise ValueError(f"Ученик {student_id} в классе {class_num} не найден.")
    return student_data


def predict_grades(student_id, class_num):
    student_data = get_student_class_data(student_id, class_num)
    if student_data.empty:
        print("Ошибка: Нет данных для ученика", student_id, "в классе", class_num)
        return [0] * 9

    prediction = model.predict(student_data)
    print("Предсказанные оценки:", prediction)  # Отладочный вывод
    return prediction


def create_risk_chart(prediction):
    """Создает график рисков на основе предсказанных оценок."""
    # Убедимся, что у нас ровно 9 оценок
    prediction = prediction[:len(subjects)]

    # Преобразуем оценки в уровни риска (5 → 1, 4 → 2, 3 → 3, 2 → 4)
    risk_levels = [5 - grade + 1 for grade in prediction]  # Теперь шкала 1-4

    fig, ax = plt.subplots(figsize=(10, 5))

    # Цвета в зависимости от уровня риска
    colors = []
    for level in risk_levels:
        if level >= 4:
            colors.append('#ff5252')  # Красный - высокий риск
        elif level >= 3:
            colors.append('#ffb74d')  # Оранжевый - средний риск
        else:
            colors.append('#66bb6a')  # Зеленый - низкий риск

    bars = ax.barh(subjects, risk_levels, color=colors, height=0.6)

    # Добавляем значения на график
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height() / 2,
                f'{width:.1f}',
                ha='left', va='center',
                fontsize=10, fontweight='bold')

    # Настройки осей
    ax.set_xlim(0, 5)
    ax.set_xticks(range(0, 6))
    ax.set_xlabel('Уровень риска (1-5)', fontsize=12)
    ax.set_title('Риски успеваемости по предметам', fontsize=14, pad=20)

    plt.tight_layout()
    return fig

def create_class_chart():
    """Создает график успеваемости класса."""
    grades = ['Отлично', 'Хорошо', 'Удовлетворительно', 'Неудовлетворительно']
    counts = [8, 9, 10, 5]

    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(grades, counts, color=['#4CAF50', '#8BC34A', '#FFC107', '#F44336'])

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{height}', ha='center', va='bottom')

    ax.set_ylabel('Количество учеников')
    ax.set_title('Статистика по 10Б классу')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=80)
    plt.close()
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"


def get_recommendations(prediction):
    """Формирует рекомендации на основе предсказанных оценок."""
    risk_subjects = [subject for subject, grade in zip(subjects, prediction) if grade in (2, 3)]

    if risk_subjects:
        if len(risk_subjects) == 1:
            return f"Подтяните знания в следующем предмете: {risk_subjects[0]}"
        else:
            return "Подтяните знания в следующих предметах: " + ", ".join(risk_subjects)
    else:
        return "Нет предметов с низкими оценками (2 или 3)."


def calculate_average_grade(prediction):
    """Вычисляет среднюю оценку."""
    return round(sum(prediction) / len(prediction), 2)


class_chart = create_class_chart()

custom_css = """
/* (Ваши существующие CSS стили остаются без изменений) */
/* Главное меню */
.main-container {
    font-family: 'Segoe UI', sans-serif;
    padding: 40px;
    max-width: 1200px;
    margin: 0 auto;
}

.first-page {
    display: flex;
    flex-direction: column;
}

.main-text {
    font-size: 52px;
    font-weight: 800;
    color: #02033B;
    margin-bottom: 30px;
    line-height: 1.2;
}

.sub-text {
    font-size: 18px;
    color: #1B1E56;
    margin-bottom: 40px;
    max-width: 80%;
}

.start-button {
    background: linear-gradient(90deg, #FFCB52, #FCA024);
    border: none;
    border-radius: 50px;
    padding: 14px 28px;
    font-size: 19px;
    font-weight: 700;
    color: black;
    cursor: pointer;
    width: fit-content;
}

/* Стили для страницы входа */
.login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 40px;
}

.login-title {
    font-size: 52px;
    font-weight: 600;
    margin-bottom: 30px;
    text-align: center;
}

.login-input {
    width: 100%;
    padding: 12px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

.login-button {
    width: 100%;
    padding: 12px;
    background-color: #000;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 15px;
}

.recovery-link {
    text-align: center;
    color: #000;
    text-decoration: underline;
    cursor: pointer;
    font-size: 14px;
    background: none !important;
    border: none !important;
}

/* Стили для страницы восстановления */
.recovery-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 40px;
}

.recovery-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 15px;
    text-align: center;
}

.recovery-text {
    text-align: center;
    margin-bottom: 30px;
    font-size: 16px;
}

.recovery-input {
    width: 100%;
    padding: 12px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

.recovery-button {
    width: 100%;
    padding: 12px;
    background-color: #000;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
}

.back-button {
    display: block;
    margin-top: 20px;
    text-align: center;
    color: #000;
    text-decoration: underline;
    cursor: pointer;
    font-size: 14px;
    background: none !important;
    border: none !important;
}

/* Стили для страницы информации */
.profile-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px;
}

.profile-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
}

.profile-section {
    margin-bottom: 30px;
}

.profile-divider {
    border-top: 1px solid #ddd;
    margin: 20px 0;
}

.analyze-button {
    background-color: #000;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    margin: 20px 0;
    display: block;
    width: 100%;
}

.grades-table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}

.grades-table th, .grades-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
}

.grades-table th {
    background-color: #f2f2f2;
}

.risk-chart-container {
    margin: 20px 0;
    width: 100%;
}

.risk-scale {
    display: flex;
    justify-content: space-between;
    width: 100%;
    max-width: 600px;
    margin: 10px auto 0;
}

.risk-scale-item {
    text-align: center;
    width: 25%;
}

.recommendations {
    background-color: #e8f5e9;
    padding: 15px;
    border-radius: 4px;
    margin-top: 20px;
}

/* Стили для страницы учителя */
.class-teacher-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px;
}

.class-teacher-title {
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 20px;
}

.class-selector {
    display: flex;
    gap: 15px;
    margin-bottom: 20px;
}

.class-selector select, .class-selector input {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

.stats-container {
    margin: 20px 0;
}

.stats-scale {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
}

.student-list {
    margin: 15px 0;
    padding: 0;
    list-style-type: none;
}

.student-list li {
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.risk-scale-numbers {
    display: flex;
    justify-content: space-between;
    width: 100px;
    margin: 10px 0;
}

footer {
    display: none !important;
}
"""
# with open("password.png", "rb") as image_file:
#     base64_str = base64.b64encode(image_file.read()).decode('utf-8')
# custom_css_base64 = f"""
# body {{
#     background-image: url('data:image/png;base64,{base64_str}') !important;;
# }}
# """
# custom_css += custom_css_base64

def show_home():
    return [
        gr.update(visible=True),  # home_page
        gr.update(visible=False),  # entry_page
        gr.update(visible=False),  # recovery_page
        gr.update(visible=False),  # student_page
        gr.update(visible=False)  # teacher_page
    ]


def show_entry():
    return [
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False)
    ]


def show_recovery():
    return [
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False)
    ]


def show_student():
    return [
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False)
    ]


def show_teacher():
    return [
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True)
    ]


def check_user(login, password):
    users_db = SavesDataUsers().get_data_user()
    for user in users_db:
        if users_db[user]["login"] == login and users_db[user]["password"] == password:
            if users_db[user]["type"] == "student":
                student_data = SavesDataStudents().get_data_student(user)
                student_id = student_data['student_id']
                class_num = 9
                try:
                    student_data = get_student_class_data(student_id, class_num)
                    prediction = model.predict(student_data)
                    print("Сырые предсказания модели:", prediction)  # Добавлено

                    prediction = prediction[:9] if len(prediction) >= 9 else prediction.tolist() + [3] * (
                                9 - len(prediction))
                    print("Обработанные оценки:", prediction)  # Добавлено

                    risk_fig = create_risk_chart(prediction)
                    recommendations = get_recommendations(prediction)
                    avg_grade = calculate_average_grade(prediction)
                    grades_html = generate_grades_html(prediction)

                    return [
                        *show_student(),
                        risk_fig,  # Возвращаем figure вместо base64
                        recommendations,
                        f"{avg_grade:.2f}",
                        prediction,
                        grades_html
                    ]
                except Exception as e:
                    raise gr.Error(f"Ошибка при анализе данных: {str(e)}")
            elif users_db[user]["type"] in ["teacher", "class_teacher", "director"]:
                return show_teacher()
    raise gr.Error("Неверный логин или пароль")


def send_recovery(email_or_phone):
    return show_entry()


def analyze_student(student_id, class_num):
    try:
        prediction = predict_grades(student_id, class_num)

        # Гарантируем 9 элементов, заменяем None на 3 (средняя оценка)
        prediction = [x if x is not None else 3 for x in prediction]
        prediction = (prediction + [3] * 9)[:9]  # Заполняем недостающие

        print("Предсказанные оценки:", prediction)  # Для отладки

        risk_fig = create_risk_chart(prediction)
        recommendations = get_recommendations(prediction)
        avg_grade = calculate_average_grade(prediction)
        grades_html = generate_grades_html(prediction)

        return [
            risk_fig,
            recommendations,
            f"{avg_grade:.2f}",
            prediction,
            grades_html
        ]
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        raise gr.Error(f"Ошибка анализа: {str(e)}")

def generate_grades_html(prediction):
    # Гарантируем 9 элементов
    prediction = (prediction + [0] * 9)[:9]

    subjects = [
        "Вероятность и статистика", "Геометрия", "Обществознание",
        "Русский язык", "Современная литература", "Труд",
        "Физ-ра", "Физика", "Химия"  # Исправлено с "Хэ" на "Химия"
    ]

    headers = "".join(f"<th>{subj}</th>" for subj in subjects)
    values = "".join(f"<td>{grade}</td>" for grade in prediction)

    return f"""
    <table class="grades-table">
        <tr>{headers}</tr>
        <tr>{values}</tr>
    </table>
    """

with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as demo:
    # Скрытые элементы для хранения данных
    current_prediction = gr.State([])

    with gr.Column(visible=True, elem_classes=["main-container"]) as home_page:
        gr.Markdown("""
        <div class="first-page">
            <div class="main-text">
                Система категоризации обучающихся<br>по уровням прогнозируемой успеваемости
            </div>
            <div class="sub-text">
                На основе данных об оценках, посещаемости и других показателях система определяет риск низкой успеваемости.
            </div>
        </div>
        """)
        start_btn = gr.Button("Начать работу!", elem_classes="start-button")

    with gr.Column(visible=False, elem_classes=["login-container"]) as entry_page:
        gr.Markdown("""<div class="login-title">Вход</div>""")
        login_input = gr.Textbox(label="", placeholder="Логин", elem_classes="login-input")
        password_input = gr.Textbox(label="", placeholder="Пароль", type="password", elem_classes="login-input")
        login_btn = gr.Button("Вход", elem_classes="login-button")
        recovery_btn_link = gr.Button("восстановить логин/пароль", elem_classes="recovery-link")

    with gr.Column(visible=False, elem_classes=["recovery-container"]) as recovery_page:
        gr.Markdown("""<div class="recovery-title">Восстановление логина/пароля</div>""")
        gr.Markdown(
            """<div class="recovery-text">Введите эл. почту или номер телефона, для отправки письма на вашу эл. почту</div>""")
        recovery_input = gr.Textbox(label="", placeholder="Эл.почта / Номер телефона", elem_classes="recovery-input")
        recovery_btn = gr.Button("Отправить", elem_classes="recovery-button")
        back_btn = gr.Button("Назад", elem_classes="back-button")

    with gr.Column(visible=False, elem_classes=["profile-container"]) as student_page:
        gr.Markdown("""<div class="profile-title">Информация о себе</div>""")

        with gr.Column(elem_classes="profile-section"):
            gr.Markdown("**ФИО**  \n**Класс**  \n**Литер класса**")
            gr.Markdown(
                "Нажмите 'Проанализировать' для начала анализа успеваемости и прогнозирования рисков по данным вашей учебы.")
            gr.Markdown("""<div class="profile-divider"></div>""")

            with gr.Row():
                class_num_input = gr.Number(label="Номер класса", value=8)
                analyze_btn = gr.Button("Проанализировать", elem_classes="analyze-button")

            gr.Markdown("""<div class="profile-divider"></div>""")

        with gr.Column(elem_classes="profile-section"):
            gr.Markdown("### Ваша успеваемость")
            avg_grade_output = gr.Textbox(label="Средняя оценка")
            grades_table = gr.HTML("""
            <table class="grades-table">
                <tr>
                    <th>Вероятность и статистика</th>
                    <th>Геометрия</th>
                    <th>Обществознание</th>
                    <th>Русский язык</th>
                    <th>Современная литература</th>
                    <th>Труд</th>
                    <th>Физ-ра</th>
                    <th>Физика</th>
                    <th>Химия</th>
                </tr>
                <tr>
                    <td>0</td><td>0</td><td>0</td><td>0</td><td>0</td>
                    <td>0</td><td>0</td><td>0</td><td>0</td>
                </tr>
            </table>
            """)
            gr.Markdown("""<div class="profile-divider"></div>""")


        class_chart = create_class_chart()

        with gr.Column(elem_classes="profile-section"):
            gr.Markdown("### Риски")
            risk_chart = gr.Plot(label="График рисков успеваемости")  # Используем Plot вместо HTML
            gr.Markdown("""
            **Шкала уровней риска:**
            - 1-2: Низкий риск
            - 3: Средний риск
            - 4-5: Высокий риск
            """)
            gr.Markdown("""<div class="profile-divider"></div>""")

        with gr.Column(elem_classes="profile-section"):
            gr.Markdown("### Рекомендации")
            recommendations_output = gr.Markdown(
                """<div class="recommendations">Нажмите "Проанализировать" для получения рекомендаций</div>""")

        back_to_main_btn = gr.Button("Назад", elem_classes="back-button")

    with gr.Column(visible=False, elem_classes=["class-teacher-container"]) as teacher_page:
        gr.Markdown("""<div class="class-teacher-title">Информация о классе</div>""")

        with gr.Column():
            gr.Markdown("Выберите класс и предмет, который необходимо проанализировать.")

            with gr.Row(elem_classes="class-selector"):
                subject = gr.Dropdown(subjects, label="Предмет")
                class_num = gr.Number(label="Класс", value=8)
                class_letter = gr.Textbox(label="Литер класса", value="Б")

            analyze_btn_teacher = gr.Button("Проанализировать", elem_classes="analyze-button")
            gr.Markdown("""<div class="profile-divider"></div>""")

        with gr.Column(elem_classes="stats-container"):
            gr.Markdown("### Статистика по классу")
            gr.HTML(f"""
            <div>
                <img src="{class_chart}" style="width: 100%; max-width: 500px; margin: 0 auto; display: block;">
                <ul style="margin-top: 20px;">
                    <li><strong>8 - Отлично</strong></li>
                    <li><strong>9 - Хорошо</strong></li>
                    <li><strong>10 - Удовлетворительно</strong></li>
                    <li><strong>5 - Неудовлетворительно</strong></li>
                </ul>
                <p>Средняя оценка по классу: <strong>Хорошо - 4</strong></p>
            </div>
            """)
            gr.Markdown("""<div class="profile-divider"></div>""")

        with gr.Column():
            gr.Markdown("### Риски")
            gr.HTML("""
            <ul class="student-list">
                <li>Иванов И.О.</li>
                <li>Воронкова Н.П.</li>
                <li>Яблочкин Е.Б.</li>
                <li>Галаниев Л.А.</li>
                <li>Чемяленко А.А.</li>
                <li>Виноградова В.С.</li>
                <li>Бананов А.К.</li>
                <li>Ананасова Е.М.</li>
            </ul>
            <div class="risk-scale-numbers">
                <span>2</span>
                <span>3</span>
                <span>4</span>
                <span>5</span>
            </div>
            """)
            gr.Markdown("""<div class="profile-divider"></div>""")

        with gr.Column():
            gr.Markdown("### Рекомендации")
            gr.Markdown("""
            <div class="recommendations">
                Подтяните знания у следующих учеников:<br>
                <strong>Иванов И.О., Воронкова Н.П., Яблочкин Е.Б., Галаниев Л.А., Чемяленко А.А.</strong>
            </div>
            """)

        back_btn_teacher = gr.Button("Назад", elem_classes="back-button")

    # Обработчики событий
    start_btn.click(show_entry, outputs=[home_page, entry_page, recovery_page, student_page, teacher_page])
    login_btn.click(check_user, inputs=[login_input, password_input],
                    outputs=[home_page, entry_page, recovery_page, student_page, teacher_page])
    recovery_btn_link.click(show_recovery, outputs=[home_page, entry_page, recovery_page, student_page, teacher_page])
    recovery_btn.click(send_recovery, inputs=[recovery_input],
                       outputs=[home_page, entry_page, recovery_page, student_page, teacher_page])
    back_btn.click(show_entry, outputs=[home_page, entry_page, recovery_page, student_page, teacher_page])
    back_to_main_btn.click(show_home, outputs=[home_page, entry_page, recovery_page, student_page, teacher_page])
    back_btn_teacher.click(show_entry, outputs=[home_page, entry_page, recovery_page, student_page, teacher_page])

    analyze_btn.click(
        fn=analyze_student,
        inputs=[gr.State(1), class_num_input],
        outputs=[
            risk_chart,
            recommendations_output,
            avg_grade_output,
            current_prediction,
            grades_table
        ]
    )

    demo.launch(share=False)
