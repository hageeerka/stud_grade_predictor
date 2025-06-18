import pandas as pd
import sqlite3
import joblib


def encode_multiclass_target(data, category, target='Mark'):
    df = data[[category, target]].copy()

    target_dummies = pd.get_dummies(df[target],
                                    prefix=category,
                                    drop_first=True)

    df = pd.concat((df, target_dummies), axis=1)

    for tg in target_dummies.columns:
        df[tg] = df.groupby(category)[tg].transform("mean")

    return df.drop(category, axis=1)


conn = sqlite3.connect('new_database_17.06.db')
cursor = conn.cursor()
df = pd.read_sql('SELECT * FROM dataset', conn)
df.drop('index', axis=1, inplace=True)
student_info = pd.read_sql('SELECT * FROM student_info', conn)
student_info.drop('index', axis=1, inplace=True)
site_user = pd.read_sql('SELECT * FROM site_user', conn)
site_user.drop('index', axis=1, inplace=True)
#df = df[((df['Class'] == 9) & (df['Period'] == 3)) | ((df['Class'] == 11) & df['Period'] == 2)]

# Преобразование в формат модели
categorical_columns = df.loc[:, df.dtypes == object].columns
one_hot = pd.get_dummies(df['Gender'], prefix='gender', drop_first=True)
df1 = pd.concat([df, one_hot], axis=1)
upd_df = df.copy()
for col in categorical_columns:
    if upd_df[col].nunique() < 4:
        one_hot = pd.get_dummies(upd_df[col], prefix=col, drop_first=True)
        upd_df = pd.concat((upd_df, one_hot), axis=1)
    else:
        mean_target = encode_multiclass_target(upd_df, col).drop('Mark', axis=1)
        upd_df = pd.concat((upd_df.drop(col, axis=1), mean_target), axis=1)
upd_df = upd_df.drop('Gender', axis=1)
# Составление предиктов
model = joblib.load('model_1.pkl')
y = model.predict(upd_df.drop(['Mark', 'Missed_Classes'], axis=1))
y = pd.DataFrame(y)
df = df.join(y)
df.columns = ['Student', 'Period', 'Gender', 'Class',
              'Subject', 'Mark', 'Is_new_sub', 'Average_grade',
              'Perform_trend', 'Missed_Classes', 'y']
df.drop('Mark', axis=1, inplace=True)

student_index = df.Student.unique()

# Генерация таблиц classes  и subjects
columns = ['number', 'letter']
classes = pd.DataFrame(
    [[8, 'А'], [8, 'Б'], [8, 'В'], [9, 'А'], [9, 'Б'], [10, 'А'], [11, 'А']
     ], columns=columns)
classes['class_id'] = classes.index
classes = classes[['class_id', 'number', 'letter']]
subjects = pd.DataFrame(df['Subject'].unique())
subjects['id'] = subjects.index
subjects = subjects[['id', 0]]
subjects.columns = ['id', 'Subject_name']

students = df[['Student', 'Subject', 'y']].copy()
students.columns = ['student_id', 'Subject_name', 'y']
students = students.join(subjects.set_index('Subject_name'), on='Subject_name')
students.drop('Subject_name', axis=1, inplace=True)
students.columns = ['student_id', 'grade', 'subject_id']
students = students[['student_id', 'subject_id', 'grade']]

first_teacher_index = student_info.shape[0] + 1
first_parent_index = student_info.shape[0] + 6
columns = ['user_id', 'student_id']

parents_user = pd.DataFrame([
    [first_parent_index, 1], [first_parent_index + 1, 2], [first_parent_index + 2, 3], [first_parent_index + 3, 4],
    [first_parent_index + 4, 5]
], columns=columns)
user_student = pd.DataFrame(site_user['user_id'].reset_index(drop=True), columns=['user_id'])
user_student['student_id'] = student_info['student_id'].reset_index(drop=True)

user_student = pd.concat([user_student, parents_user])
user_student.dropna(inplace=True)
columns = ['user_id', 'class_id']
teacher_class = pd.DataFrame([
    [first_teacher_index, 1], [first_teacher_index, 2], [first_teacher_index, 3], [first_teacher_index, 6],
    [first_teacher_index + 1, 2], [first_teacher_index + 2, 3], [first_teacher_index + 3, 4],
    [first_teacher_index + 4, 5]
], columns=columns)

columns = ['user_id', 'subject_id']
teacher_subject = pd.DataFrame([
    [first_teacher_index, 0], [first_teacher_index + 1, 21], [first_teacher_index + 1, 8],
    [first_teacher_index + 1, 12], [first_teacher_index + 2, 13], [first_teacher_index + 3, 9],
    [first_teacher_index + 4, 18]
], columns=columns)

subjects.columns = ['subject_id', 'name']
cur = conn.cursor()
cur.executescript("""
DROP TABLE IF EXISTS teacher_subject;
DROP TABLE IF EXISTS teacher_class;
DROP TABLE IF EXISTS user_student;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS classes;
""")
subjects.to_sql('subjects', con=conn)
classes.to_sql('classes', con=conn)
teacher_subject.to_sql('teacher_subject', con=conn)
teacher_class.to_sql('teacher_class', con=conn)
user_student.to_sql('user_student', con=conn)
students.to_sql('students', con=conn)
cur.executescript("""
-- Поддержка внешних ключей
PRAGMA foreign_keys = ON;

-- Удалим временные таблицы, если они остались от прошлых запусков
DROP TABLE IF EXISTS teacher_subject_old;
DROP TABLE IF EXISTS teacher_class_old;
DROP TABLE IF EXISTS user_student_old;
DROP TABLE IF EXISTS students_old;
DROP TABLE IF EXISTS student_info_old;
DROP TABLE IF EXISTS site_user_old;
DROP TABLE IF EXISTS subjects_old;
DROP TABLE IF EXISTS classes_old;

--  Пересоздание subjects
ALTER TABLE subjects RENAME TO subjects_old;
CREATE TABLE subjects (
    subject_id INTEGER PRIMARY KEY,
    name TEXT
);
INSERT INTO subjects (subject_id, name)
SELECT subject_id, name FROM subjects_old;
DROP TABLE subjects_old;

-- Пересоздание site_user
ALTER TABLE site_user RENAME TO site_user_old;
CREATE TABLE site_user (
    user_id INTEGER PRIMARY KEY,
    login TEXT,
    password TEXT,
    type TEXT,
    phone INTEGER,
    email TEXT
);
INSERT INTO site_user (user_id, login, password, type, phone, email)
SELECT user_id, login, password, type, phone, email FROM site_user_old;
DROP TABLE site_user_old;

-- Пересоздание classes
ALTER TABLE classes RENAME TO classes_old;
CREATE TABLE classes (
    class_id INTEGER PRIMARY KEY,
    number INTEGER,
    letter TEXT
);
INSERT INTO classes (class_id, number, letter)
SELECT class_id, number, letter FROM classes_old;
DROP TABLE classes_old;

--  Пересоздание student_info
ALTER TABLE student_info RENAME TO student_info_old;
CREATE TABLE student_info (
    student_id INTEGER PRIMARY KEY,
    surname TEXT,
    name TEXT,
    patronymic TEXT,
    class_id INTEGER,
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);

DELETE FROM student_info_old
WHERE class_id NOT IN (SELECT class_id FROM classes);
INSERT INTO student_info (student_id, surname, name, patronymic, class_id)
SELECT student_id, surname, name, patronymic, class_id FROM student_info_old;
DROP TABLE student_info_old;

--  Пересоздание students
ALTER TABLE students RENAME TO students_old;
CREATE TABLE students (
    student_id INTEGER,
    subject_id INTEGER,
    grade INTEGER,
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
    FOREIGN KEY (student_id) REFERENCES student_info(student_id)
);

DELETE FROM students_old
WHERE subject_id NOT IN (SELECT subject_id FROM subjects)
   OR student_id NOT IN (SELECT student_id FROM student_info);
INSERT INTO students (student_id, subject_id, grade)
SELECT student_id, subject_id, grade FROM students_old;
DROP TABLE students_old;

-- Пересоздание user_student
ALTER TABLE user_student RENAME TO user_student_old;

CREATE TABLE user_student (
    user_id INTEGER,
    student_id INTEGER,
    PRIMARY KEY (user_id, student_id),
    FOREIGN KEY (user_id) REFERENCES site_user(user_id),
    FOREIGN KEY (student_id) REFERENCES student_info(student_id)
);

DELETE FROM user_student_old
WHERE user_id NOT IN (SELECT user_id FROM site_user)
   OR student_id NOT IN (SELECT student_id FROM students);
INSERT INTO user_student (user_id, student_id)
SELECT user_id, student_id FROM user_student_old;
DROP TABLE user_student_old;

-- Пересоздание teacher_subject
ALTER TABLE teacher_subject RENAME TO teacher_subject_old;
CREATE TABLE teacher_subject (
    user_id INTEGER,
    subject_id INTEGER,
    PRIMARY KEY (user_id, subject_id),
    FOREIGN KEY (user_id) REFERENCES site_user(user_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);
DELETE FROM teacher_subject_old
WHERE user_id NOT IN (SELECT user_id FROM site_user)
   OR subject_id NOT IN (SELECT subject_id FROM subjects);
INSERT INTO teacher_subject (user_id, subject_id)
SELECT user_id, subject_id FROM teacher_subject_old;
DROP TABLE teacher_subject_old;

-- Пересоздание teacher_class
ALTER TABLE teacher_class RENAME TO teacher_class_old;
CREATE TABLE teacher_class (
    user_id INTEGER,
    class_id INTEGER,
    PRIMARY KEY (user_id, class_id),
    FOREIGN KEY (user_id) REFERENCES site_user(user_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);
DELETE FROM teacher_class_old
WHERE user_id NOT IN (SELECT user_id FROM site_user)
   OR class_id NOT IN (SELECT class_id FROM classes);
INSERT INTO teacher_class (user_id, class_id)
SELECT user_id, class_id FROM teacher_class_old;
DROP TABLE teacher_class_old;
-- внешние ключи
PRAGMA foreign_keys = ON;
""")
