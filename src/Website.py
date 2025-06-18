import gradio as gr
import matplotlib.pyplot as plt
# from io import BytesIO
# import base64
# import pandas as pd
# import joblib
import warnings
from connection_to_BD import SavesDataUsers, SavesDataStudents, Subjects, SavesDataTeacher, SavesDataClasses
from functools import lru_cache
import matplotlib

# from twilio.rest import Client
# import smtplib
# from email.message import EmailMessage

matplotlib.use('Agg')
warnings.filterwarnings("ignore")

subjects = Subjects().take_subjects()


def check_recovery_method(method):
    try:
        error = 12 / 0
    except:
        raise gr.Error(
            f"Данная функция сейчас,к сожалению, не работает :(, ваш способ восстановления: {method}")


# def get_student_class_data(student_id, class_num):
#     student_data = df[(df['Student'] == student_id) & (df['Class'] == class_num[0])]
#     # print(student_data.head())
#     if student_data.empty:
#         raise ValueError(f"Ученик {student_id} в классе {class_num[0], class_num[1]} не найден.")
#     return student_data
#
#

def update_subject_teacher(user_id):
    return gr.update(choices=SavesDataTeacher().get_subjects_teacher(user_id=user_id))


def update_classes_teacher(user_id):
    return gr.update(choices=SavesDataTeacher().get_classes_teacher(user_id=user_id))


def predict_grades(student_id):
    return SavesDataStudents().take_grades(student_id)


def predict_status_class(class_id, subject_id):
    class_data = SavesDataTeacher().get_class_teacher(class_id, subject_id)
    dict_class_data = {'Отлично': 0, 'Хорошо': 0, 'Удовл': 0, 'Неудовл': 0}
    for student in class_data:
        if student[4] == 5:
            dict_class_data['Отлично'] += 1
        elif student[4] == 4:
            dict_class_data['Хорошо'] += 1
        elif student[4] == 3:
            dict_class_data['Удовл'] += 1
        else:
            dict_class_data['Неудовл'] += 1
    return dict_class_data


def predict_status_selected_classes(class_main, other_classes, subject_id):
    other_classes.append(class_main)
    class_data = {}
    for class_selected in other_classes:
        class_data[str(class_selected[0]) + class_selected[1]] = \
            SavesDataClasses().take_score_class_by_subject(class_selected[0], class_selected[1], subject_id)

    return class_data


# def predict_hists_status_classes_director(splitting_classes, lst_subjects):
#     classes_score = {}
#     for i in range(len(splitting_classes)):
#
#         num = splitting_classes[i][0]
#         letter = splitting_classes[i][1]
#         classes_score[str(num) + letter] = SavesDataClasses().take_score_class_by_subject(num, letter)
#         # print(classes_score)
#     return classes_score
def predict_status_classes_director(splitting_classes, lst_classes):
    classes_score = {}
    classes_score_subjects = {}
    for i in range(len(splitting_classes)):
        num = splitting_classes[i][0]
        letter = splitting_classes[i][1]
        data = SavesDataClasses().take_score_class_all_subjects(num, letter, lst_classes)
        classes_score[str(num) + letter] = data[0]
        classes_score_subjects[str(num) + letter] = data[1]
        # print(classes_score)
    return [classes_score, classes_score_subjects]


def create_hists_status_classes_director(classes_score):
    """
    classes_score = {
        '9А': [('математика', 4.32), ('английский', 3.33)],
        '9Б': [('математика', 2.32), ('английский', 5.0)]
    }
    """
    subjects_bar = list({subject for class_data in classes_score.values() for subject, _ in class_data})
    grouped_data = {}
    for cls, scores in classes_score.items():
        score_dict = dict(scores)
        grouped_data[cls] = [score_dict.get(subj, 0) for subj in subjects_bar]

    bar_width = 0.2
    index = range(len(subjects_bar))

    fig, ax = plt.subplots(figsize=(10, 6))
    for i, cls in enumerate(classes_score.keys()):
        ax.bar([x + i * bar_width for x in index], grouped_data[cls], width=bar_width, label=cls)

    ax.set_xlabel('Предметы')
    ax.set_ylabel('Средний балл')
    ax.set_title('Успеваемость по классам и предметам')
    ax.set_xticks([i + bar_width for i in index])
    ax.set_xticklabels(subjects_bar, rotation=45, ha='right')
    ax.legend(title='Классы')

    plt.tight_layout()
    return fig


def create_circle_status_classes_director(classes_score):
    # prediction = dict(classes_score)
    prediction = classes_score
    counts = []
    labels = []
    for key in prediction.keys():
        labels.append(key)
        counts.append(prediction[key])

    fig, ax = plt.subplots(figsize=(10, 5))

    wedges, texts, autotexts = ax.pie(
        counts,
        labels=labels,
        startangle=90,
        autopct=lambda pct: f"{(pct * sum(counts) / 100):.2f}",
        pctdistance=0.85,
        textprops={'color': "w", 'fontsize': 12},
        wedgeprops=dict(width=0.4)
    )

    fig.legend(wedges, labels,
               title="Успеваемость",
               loc="center right",
               bbox_to_anchor=(1.0, 0.5),
               prop={'size': 12},
               fancybox=True)

    plt.setp(texts, color='white')
    plt.setp(autotexts, color='white')

    ax.axis('equal')
    ax.set_title("Соотношение средней оценки по классу", fontsize=14)
    plt.subplots_adjust(right=0.7)

    return fig


def create_risk_chart_teacher(class_id, subject_id):
    class_data = sorted(SavesDataTeacher().get_class_teacher(class_id, subject_id), key=lambda item: item[4],
                        reverse=True)
    risk_levels = []
    fullname_student = []
    for grade in class_data:
        fullname_student.append(grade[1] + ' ' + grade[2] + ' ' + grade[3])
        risk_levels.append(grade[4])

    fig, ax = plt.subplots(figsize=(10, 5))
    # colors = ['#ff5252' if r >= 4 else '#ffb74d' if r >= 3 else '#66bb6a' for r in risk_levels]
    ax.barh(fullname_student, risk_levels)
    ax.set_xlim(0, 5)
    ax.set_xticks(range(0, 6))
    ax.set_xlabel('Оценки учеников', fontsize=12)
    ax.set_title('Успеваемость по классу', fontsize=14, pad=20)
    plt.tight_layout()
    return fig


@lru_cache(maxsize=32)
def create_risk_chart(prediction_tuple):
    prediction = dict(prediction_tuple)
    prediction = dict(sorted(prediction.items(), key=lambda item: item[1], reverse=True))
    risk_levels = [5 - grade + 1 for grade in prediction.values()]
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ['#ff5252' if r >= 4 else '#ffb74d' if r >= 3 else '#66bb6a' for r in risk_levels]
    ax.barh(list(prediction.keys()), risk_levels, color=colors)
    ax.set_xlim(0, 5)
    ax.set_xticks(range(0, 6))
    ax.set_xlabel('Уровень риска (1-5)', fontsize=12)
    ax.set_title('Риски успеваемости по предметам', fontsize=14, pad=20)
    plt.tight_layout()
    return fig


@lru_cache(maxsize=32)
def create_status_class(counts_tuple):
    prediction = dict(counts_tuple)
    labels = ['Отлично', 'Хорошо', 'Удовлетворительно', 'Неудовлетворительно']
    counts = [prediction['Отлично'], prediction['Хорошо'], prediction['Удовл'], prediction['Неудовл']]
    colors = ['#4CAF50', '#FFEB3B', '#FF9800', '#F44336']

    fig, ax = plt.subplots(figsize=(10, 5))

    wedges, texts, autotexts = ax.pie(
        counts,
        labels=labels,
        startangle=90,
        colors=colors,
        autopct=lambda pct: f'{int(round(pct * sum(counts) / 100))}',
        pctdistance=0.85,
        textprops={'color': "w", 'fontsize': 12},
        wedgeprops=dict(width=0.4)
    )

    fig.legend(wedges, labels,
               title="Успеваемость",
               loc="center right",
               bbox_to_anchor=(1.0, 0.5),
               prop={'size': 12},
               fancybox=True)

    plt.setp(texts, color='white')
    plt.setp(autotexts, color='white')

    ax.axis('equal')
    ax.set_title("Распределение успеваемости", fontsize=14)
    plt.subplots_adjust(right=0.7)

    return fig


def create_status_with_other_classes(prediction):
    labels = list(prediction.keys())
    counts = [prediction[count] for count in prediction]

    fig, ax = plt.subplots(figsize=(10, 5))

    wedges, texts, autotexts = ax.pie(
        counts,
        labels=labels,
        startangle=90,
        autopct=lambda pct: f"{(pct * sum(counts) / 100):.2f}",
        pctdistance=0.85,
        textprops={'color': "w", 'fontsize': 12},
        wedgeprops=dict(width=0.4)
    )

    fig.legend(wedges, labels,
               title="Успеваемость",
               loc="center right",
               bbox_to_anchor=(1.0, 0.5),
               prop={'size': 12},
               fancybox=True)

    plt.setp(texts, color='white')
    plt.setp(autotexts, color='white')

    ax.axis('equal')
    ax.set_title("Распределение успеваемости", fontsize=14)
    plt.subplots_adjust(right=0.7)

    return fig


def get_recommendations(prediction):
    risk_subjects = []
    for subj_grade in prediction:
        if prediction[subj_grade] <= 3:
            risk_subjects.append(subj_grade)

    if risk_subjects:
        return f"Подтяните знания в следующих предметах: {', '.join(risk_subjects)}"
    return "Нет предметов с низкими оценками."


def get_recommendations_teacher(class_id, subject_id):
    students = sorted(SavesDataTeacher().get_class_teacher(class_id, subject_id), key=lambda item: item[4])
    risk_students = [f'{students[student][1]} {students[student][2]} {students[student][3]}' for student in range(3)]

    if risk_students:
        return f"Подтяните знания у следующих учеников: {', '.join(risk_students)}"
    return "Нет предметов с низкими оценками."


def calculate_average_grade(prediction):
    return round(sum(prediction.values()) / len(prediction), 2)


def generate_grades_html(prediction):
    # prediction = dict(prediction)
    headers = ''
    values = ''
    for subj_grad in prediction:
        headers += f"<th>{subj_grad}</th>"
        values += f"<td>{prediction[subj_grad]}</td>"
    return f"""
    <div class="grades-table-container">
        <table class="grades-table">
            <tr>{headers}</tr>
            <tr>{values}</tr>
        </table>
    </div>
    """


custom_css = """
.text{
    color: #000000 !important;
}


.logo-btn {
    background: none !important;
    border: none !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 0 -90px 0 0!important;
    margin: 0 !important;
}
.logo {
    font-size: 24px;
    font-weight: bold;
    color: #02033B;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 10px;
}
.logo-btn-circle{
    background: linear-gradient(90deg, #ffe657, #FC6F11) !important;
    width: 30px !important;
    height: 30px !important;
    border-radius: 50% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
.logo-btn-text{
    font-weight: bold !important;
    font-size: 25px !important;
    color: #02033b !important;
    font-weight: normal !important;
}
.logo-btn:hover .logo .logo-btn-text{
    color: rgb(6 8 155) !important;
}
.logo-btn:hover .logo .logo-btn-circle{
    background: linear-gradient(60deg, #ffe657, #FC6F11) !important;
}

.logo-btn:active .logo .logo-btn-text{
    color: #0c97ce !important;
}
.logo-btn:active .logo .logo-btn-circle{
    background: linear-gradient(60deg, #ffdc13, #ff4e00) !important;
}

.full-width {
    width: 100%;
    padding: 0;
    margin: 0;
}
.app.svelte-wpkpf6.svelte-wpkpf6:not(.fill_width) {
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important; 
    background: #fff;
}
.main-container {
    font-family: 'Segoe UI', sans-serif;
    padding: 40px;
    max-width: 1200px;
    margin: 0 auto;
}

.header {
    display: flex;
    align-items: center;
    justify-content: center; /* Центрирует содержимое */
    padding: 15px 0; /* Убираем отступы по бокам */
    background-color: #F3F8FF;
    position: sticky;
    top: 0;
    z-index: 1000;
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
    background: linear-gradient(90deg, #ffda52, #fc6224);
    border: none;
    border-radius: 50px;
    padding: 14px 28px;
    font-size: 19px;
    font-weight: 700;
    color: black;
    cursor: pointer;
    width: fit-content;
    transition: background 2s ease;
}
.start-button:hover {
    background: linear-gradient(90deg, #fffa52, #fc7224);
}
.start-button:active{
    background: linear-gradient(90deg, #faf305, #fc5624);
}
.text{
    color:#1f2937;

}
.input{
    border: 1px solid rgb(221, 221, 221);
    background: #fff;
}


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
html,
body,
.gradio-container,
.svelte-wpkpf6,
.block,
.form,
.markdown,
.label,
.textbox,
.dropdown,
.button,
.panel {
    background-color: #ffffff !important;
    color: #000000 !important;
}

:root {
    --background-fill-primary: #ffffff !important;
    --background-fill-secondary: #f7f7f7 !important;
    --color-text-primary: #000000 !important;
    --color-accent: #000000 !important;
    --color-accent-soft: #f0f0f0 !important;
}
.gradio-container-4-44-1 .prose * {
    color: #02033b !important;
}
.grades-table-container {
    overflow-x: auto;
    white-space: nowrap;
}

.grades-table {
    width: max-content; 
    border-collapse: collapse;
    margin: 20px 0;
}
.grades-table th,
.grades-table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
}
.grades-table th {
    background-color: #f2f2f2;
}
@media (max-width: 768px) {
    .main-container {
        justify-content: center;
    }
    .main-text {
        text-align: center;
        font-size: 32px;
    }
    .sub-text {
        font-size: 16px;
        text-align: center;
        max-width: 100% !important;
    }
    .start-button {
    background: linear-gradient(90deg, #ffda52, #fc6224);
    border: none;
    border-radius: 50px;
    padding: 14px 28px;
    font-size: 19px;
    font-weight: 700;
    color: black;
    cursor: pointer;
    display: block;
    margin: 20px auto 0 auto;
    text-align: center;
    width: fit-content;
    transition: background 2s ease;
}
}
"""


def show_home():
    return [
        gr.update(visible=True),  # home_page
        gr.update(visible=False),  # entry_page
        gr.update(visible=False),  # recovery_page
        gr.update(visible=False),  # student_page
        gr.update(visible=False),  # teacher_page
        gr.update(visible=False)  # director_page
    ]


def show_entry():
    return [
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
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
        gr.update(visible=False),
        gr.update(visible=False)
    ]


def show_student():
    return [
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False)
    ]


def show_teacher():
    return [
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False)
    ]


def show_director():
    return [
        gr.update(visible=False),
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
            if users_db[user]["type"] in ["student", "parent"]:
                stud_data = SavesDataStudents().get_data_student(user_id=user)
                student_id = stud_data[0]
                class_num = stud_data[4:]
                if users_db[user]["type"] == 'student':
                    user_info_text = (
                        f"**Ваша роль:** Ученик/ца<br>"
                        f"**ФИО:** {stud_data[1]} {stud_data[2]} {stud_data[3]}<br>"
                        f"**Класс:** {stud_data[4]}{stud_data[5]}"
                    )
                else:
                    user_info_text = (
                        f"**Ваша роль:** Родитель<br>"
                        f"**ФИО ученика/ученицы:** {stud_data[1]} {stud_data[2]} {stud_data[3]}<br>"
                        f"**Класс:** {stud_data[4]}{stud_data[5]}"
                    )
                return [
                    *show_student(),
                    user_info_text,
                    user,
                    student_id,
                    class_num,
                    [], None, None, None
                ]
            elif users_db[user]["type"] == "teacher":
                user_info_text = f"**Ваша роль:** Учитель<br>"
                subjects_teacher_ent = SavesDataTeacher().get_subjects_teacher(user_id=user)
                class_for_teacher = SavesDataTeacher().get_classes_teacher(user_id=user)
                return [
                    *show_teacher(),
                    user_info_text,
                    user,
                    None,
                    None,
                    subjects_teacher_ent,
                    gr.update(choices=subjects_teacher_ent, visible=True),
                    class_for_teacher,
                    gr.update(choices=class_for_teacher, visible=True)
                ]
            elif users_db[user]['type'] == 'director':
                print('Director')
                user_info_text = f"**Ваша роль:** Директор<br>"
                subjects_teacher_ent = SavesDataTeacher().get_subjects_teacher(user_id=user)

                return [
                    *show_director(),
                    user_info_text,
                    user,
                    None,
                    None,
                    subjects_teacher_ent,
                    gr.update(choices=subjects_teacher_ent, visible=True),
                    None, None
                ]
    raise gr.Error("Неверный логин или пароль")


def analyze_student(student_id):
    try:
        prediction = predict_grades(student_id)
        prediction_tuple = tuple(prediction.items())
        risk_fig = create_risk_chart(prediction_tuple)
        recommendations = get_recommendations(prediction)
        avg_grade = calculate_average_grade(prediction)
        grades_html = generate_grades_html(prediction)
        return [
            risk_fig,
            gr.Markdown(f"<div class='recommendations'>{recommendations}</div>"),
            avg_grade,
            grades_html,
            prediction
        ]
    except Exception as e:
        raise gr.Error(f"Ошибка анализа: {str(e)}")


def analyze_teacher(subject, class_selected):
    try:
        sub_id = Subjects().get_id_subject(subject)
        if sub_id is None:
            raise ValueError(f"Предмет '{subject}' не найден в базе данных")
        class_num = class_selected[:len(class_selected) - 1]
        class_letter = class_selected[len(class_selected) - 1]
        class_id = SavesDataClasses().take_id_class(class_num, class_letter)

        class_status_data = predict_status_class(class_id, sub_id)
        counts_tuple = tuple(class_status_data.items())
        status_class = create_status_class(counts_tuple)
        risk_class = create_risk_chart_teacher(class_id, sub_id)
        recommendations = get_recommendations_teacher(class_id, sub_id)

        return [
            status_class,
            risk_class,
            gr.Markdown(f"<div class='recommendations'>{recommendations}</div>"),
        ]
    except Exception as e:
        raise gr.Error(f"Ошибка анализа: Возможно у вас нет доступа к данному предмету или классу")


def analyze_director(subject, class_main, other_classes):
    try:
        class_num = class_main[:len(class_main) - 1]
        class_letter = class_main[len(class_main) - 1]
        sub_id = Subjects().get_id_subject(subject)
        if sub_id is None:
            raise ValueError(f"Предмет '{subject}' не найден в базе данных")
        class_id = SavesDataClasses().take_id_class(class_num, class_letter)

        class_status_data = predict_status_class(class_id, sub_id)
        counts_tuple = tuple(class_status_data.items())
        status_class = create_status_class(counts_tuple)
        if other_classes:
            splitting_classes = [(int(class_name[:len(class_name) - 1]), class_name[len(class_name) - 1]) for class_name
                                 in
                                 other_classes]
            status_with_other_classes_data = predict_status_selected_classes((class_num, class_letter),
                                                                             splitting_classes, sub_id)
        else:
            status_with_other_classes_data = {class_main: sum(class_status_data.values())}

        status_with_other_classes = create_status_with_other_classes(status_with_other_classes_data)
        return [status_class, status_with_other_classes]

    except Exception as e:
        raise gr.Error(f"Ошибка анализа: Возможно у вас нет доступа к данному предмету или классу")


def analyze_director_all_classes(lst_classes, lst_subjects):  # по возможности оптимизировать
    try:
        splitting_classes = [(int(class_name[:len(class_name) - 1]), class_name[len(class_name) - 1]) for class_name in
                             lst_classes]
        data_classes = predict_status_classes_director(splitting_classes, lst_subjects)
        build_circle_plot = create_circle_status_classes_director(data_classes[0])
        build_hists = create_hists_status_classes_director(data_classes[1])
        return [build_circle_plot, build_hists]

    except Exception as e:
        raise gr.Error(f"Ошибка анализа: Возможно у вас нет доступа к данному предмету или классу")


with gr.Blocks(css=custom_css, theme=gr.themes.Base()) as demo:
    current_user_id = gr.State()
    classes = SavesDataClasses().take_name_all_classes()  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    navigate_to_home_btn = gr.Button("Перейти на главную", visible=False, elem_id="navigate_to_home_btn")

    logo_html = gr.HTML("""
        <div class="header full-width">
            <button onclick="document.getElementById('navigate_to_home_btn').click()" class="logo-btn">
                <div class="logo">
                    <span class="logo-btn-circle"></span><span class="logo-btn-text">Aristhesis</span>
                </div>
            </button>
        </div>
    """)

    with gr.Column(visible=True, elem_classes=["main-container"]) as home_page:
        gr.Markdown("""
        <div class="first-page">
            <div class="main-text">Система категоризации обучающихся<br>по уровням прогнозируемой успеваемости</div>
            <div class="sub-text">На основе данных об оценках, посещаемости и других показателях система определяет риск низкой успеваемости.</div>
        </div>
        """)
        start_btn = gr.Button("Начать работу!", elem_classes="start-button")

    with gr.Column(visible=False, elem_classes=["login-container"]) as entry_page:
        gr.Markdown("<div class='login-title'>Вход</div>")
        login_input = gr.Textbox(label="", placeholder="Логин", elem_classes="login-input")
        password_input = gr.Textbox(label="", placeholder="Пароль", type="password", elem_classes="login-input")
        login_btn = gr.Button("Вход", elem_classes="login-button")
        recovery_link = gr.Button("восстановить логин/пароль", elem_classes="recovery-link")

    with gr.Column(visible=False, elem_classes=["recovery-container"]) as recovery_page:
        gr.Markdown("""<div class="recovery-title">Восстановление логина/пароля</div>""")
        gr.Markdown(
            """<div class="recovery-text">Введите эл. почту или номер телефона, для отправки письма на вашу эл. почту</div>""")
        recovery_input = gr.Textbox(label="", placeholder="Эл.почта / Номер телефона", elem_classes="recovery-input")
        recovery_btn = gr.Button("Отправить", elem_classes="recovery-button")

    with gr.Column(visible=False, elem_classes=["profile-container"]) as student_page:
        current_student_id = gr.State()
        current_class = gr.State()
        gr.Markdown("<div class='profile-title'>Информация о себе</div>")
        user_info_display = gr.Markdown(elem_classes="student-info", show_label=False)
        analyze_btn = gr.Button("Проанализировать", elem_classes="analyze-button")

        avg_grade_output = gr.Textbox(label="Средняя оценка")
        grades_table = gr.HTML("")
        gr.Markdown("### Ваша успеваемость")
        risk_chart = gr.Plot(label="Риски успеваемости")
        gr.Markdown("### Риски")
        gr.Markdown("""
                        **Шкала уровней риска:**
                        - 1-2: Низкий риск
                        - 3: Средний риск
                        - 4-5: Высокий риск
                        """)
        gr.Markdown("### Рекомендации")
        recommendations_output = gr.Markdown("")

    with gr.Column(visible=False, elem_classes=["class-teacher-container"]) as teacher_page:
        gr.Markdown("""<div class="class-teacher-title">Информация о классе</div>""")

        with gr.Column():
            gr.Markdown("Выберите класс и предмет, который необходимо проанализировать.")

            with gr.Row(elem_classes="class-selector"):
                subject_teacher = gr.Dropdown(choices=[], label="Предмет", interactive=True)
                classes_teacher = gr.Dropdown(choices=[], label="Класс", interactive=True)
                # classes_teacher = gr.Dropdown(choices=[], label="Класс", interactive=True)

            analyze_btn_teacher = gr.Button("Проанализировать", elem_classes="analyze-button")
            gr.Markdown("""<div class="profile-divider"></div>""")

            gr.Markdown("### Статистика класса")
            current_status_class = gr.Plot()
            gr.Markdown("### Риски")
            risk_class_teacher = gr.Plot()
            gr.Markdown("### Рекомендации")
            recommendations_output_teacher = gr.Markdown("")

    with gr.Column(visible=False, elem_classes=["class-teacher-container"]) as director_page:
        gr.Markdown("""<div class="class-teacher-title">Информация о классе (Директор)</div>""")

        with gr.Column():
            gr.Markdown("Выберите класс и предмет, который необходимо проанализировать.")

            with gr.Row(elem_classes="class-selector"):
                subject_director = gr.Dropdown(Subjects().take_subjects(), label="Предмет")
                main_selected_class = gr.Dropdown(
                    choices=classes,
                    label="Основной класс",
                    multiselect=False
                )
                other_selected_classes = gr.Dropdown(
                    choices=classes,
                    label="Остальные классы",
                    multiselect=True
                )

            analyze_btn_director_one = gr.Button("Проанализировать", elem_classes="analyze-button")
            gr.Markdown("""<div class="profile-divider"></div>""")

            gr.Markdown("### Статистика класса")
            current_status_class_director = gr.Plot()
            gr.Markdown("### Статистика класса относительно других")
            current_status_class_director_other = gr.Plot()

        gr.Markdown(
            """<div class="class-teacher-title">Выберите классы и предметы, которые необходимо сравнить</div>""")
        with gr.Column():
            with gr.Row(elem_classes="class-selector"):
                selected_classes = gr.Dropdown(
                    choices=classes,
                    label="Выберите классы",
                    multiselect=True
                )
                subject_director_multi = gr.Dropdown(
                    choices=Subjects().take_subjects(),
                    label="Выберите предметы",
                    multiselect=True
                )
            analyze_btn_director_all = gr.Button("Проанализировать", elem_classes="analyze-button")
            status_all_classes_circle = gr.Plot()
            status_all_classes_bar = gr.Plot()

    start_btn.click(
        show_entry,
        outputs=[home_page, entry_page, recovery_page, student_page, teacher_page, director_page]
    )

    recovery_link.click(
        show_recovery,
        outputs=[home_page, entry_page, recovery_page, student_page, teacher_page, director_page]
    )

    recovery_btn.click(
        fn=check_recovery_method,
        inputs=[recovery_input]
    )

    login_btn.click(
        fn=check_user,
        inputs=[login_input, password_input],
        outputs=[
            home_page, entry_page, recovery_page, student_page, teacher_page, director_page,
            user_info_display, current_user_id, current_student_id, current_class,
            subject_teacher, classes_teacher
        ]
    ).then(

        fn=update_classes_teacher,
        inputs=[current_user_id],
        outputs=[classes_teacher]
    )

    analyze_btn_teacher.click(
        fn=analyze_teacher,
        inputs=[subject_teacher, classes_teacher],
        outputs=[
            current_status_class,
            risk_class_teacher,
            recommendations_output_teacher,
        ]
    )
    analyze_btn_director_one.click(
        fn=analyze_director,
        inputs=[subject_director, main_selected_class, other_selected_classes],
        outputs=[current_status_class_director, current_status_class_director_other]
    )

    analyze_btn_director_all.click(
        fn=analyze_director_all_classes,
        inputs=[selected_classes, subject_director_multi],
        outputs=[status_all_classes_circle, status_all_classes_bar]
    )

    analyze_btn.click(
        fn=analyze_student,
        inputs=[current_student_id],
        outputs=[
            risk_chart,
            recommendations_output,
            avg_grade_output,
            grades_table,
            gr.State()
        ]
    )

    navigate_to_home_btn.click(
        fn=show_home,
        inputs=[],
        outputs=[home_page, entry_page, recovery_page, student_page, teacher_page, director_page]
    )
    # classes_teacher.change(
    #     fn=update_classes_teacher,
    #     inputs=[current_user_id],
    #     outputs=[classes_teacher]
    # )
    subject_teacher.change(
        fn=update_subject_teacher,
        inputs=[current_user_id],
        outputs=[subject_teacher]
    )

print(gr.__version__)
demo.launch(share=True)
