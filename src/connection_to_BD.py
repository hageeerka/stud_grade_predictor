import sqlite3
import gradio as gr


class Saves:
    def __init__(self):
        self.file_settings = sqlite3.connect('Database.db')
        self.cursor = self.file_settings.cursor()

    # def __del__(self):
    #     self.file_settings.close()

    def add_column(self):
        self.cursor.execute('''ALTER TABLE student 
                                        ADD COLUMN surname TEXT NOT NULL DEFAULT '' ''')
        self.cursor.execute('''ALTER TABLE student 
                                       ADD COLUMN name TEXT NOT NULL DEFAULT '' ''')
        self.cursor.execute('''ALTER TABLE student 
                                               ADD COLUMN patronymic TEXT NOT NULL DEFAULT '' ''')


class Subjects(Saves):
    def take_subjects(self):
        self.cursor.execute(f"SELECT name FROM subjects")
        subjects_name = self.cursor.fetchall()
        lst_sub = []
        for subject in subjects_name:
            lst_sub.append(subject[0])
        return lst_sub

    def get_id_subject(self, name):
        try:
            self.cursor.execute("SELECT subject_id FROM subjects WHERE name = ?", (name,))
            result = self.cursor.fetchone()

            if result:
                return result[0]
            else:
                # Предмет не найден
                print(f"Предмет '{name}' не найден в базе данных")
                print(f"Доступные предметы: {self.take_subjects()}")
                return None
        except Exception as e:
            print(f"Ошибка при поиске предмета '{name}': {str(e)}")
            return None


class SavesDataUsers(Saves):

    def get_data_user(self):
        self.cursor.execute('''SELECT * FROM site_user''')
        columns = [column[0] for column in self.cursor.description]
        users = {}
        for row in self.cursor.fetchall():
            user_dict = dict(zip(columns, row))
            users[user_dict['user_id']] = user_dict

        return users


class SavesDataClasses(Saves):
    def get_id_classes(self):
        self.cursor.execute(f"SELECT * FROM classes")
        result = self.cursor.fetchall()
        return result

    def take_id_class(self, num, letter):
        self.cursor.execute(f"SELECT class_id FROM classes where number=? and letter=?", (num, letter))
        result = self.cursor.fetchone()
        return result[0]

    def take_name_all_classes(self):
        self.cursor.execute(f"SELECT number, letter FROM classes ")
        result = self.cursor.fetchall()
        classes_lst = []
        for class_n in result:
            classes_lst.append(str(class_n[0]) + str(class_n[1]))

        return classes_lst

    def take_score_class_by_subject(self, num, letter, subject_id):
        self.cursor.execute(f"SELECT class_id FROM classes where number=? and letter=?", (num, letter))
        class_id = self.cursor.fetchone()[0]
        query = """
                    SELECT st.grade
                    FROM student_info si
                    JOIN students st ON si.student_id = st.student_id
                    WHERE si.class_id = ? AND st.subject_id = ?
                """
        self.cursor.execute(query, (class_id, subject_id))
        students_grades = self.cursor.fetchall()
        score = 0
        len_score = 0
        for student_grade in students_grades:
            score += student_grade[0]
            len_score += 1
        return score / len_score

    def take_score_class_all_subjects(self, num, letter, subjects):
        self.cursor.execute(f"SELECT class_id FROM classes where number=? and letter=?", (num, letter))
        class_id = self.cursor.fetchone()[0]
        query = """
                            SELECT st.grade
                            FROM student_info si
                            JOIN students st ON si.student_id = st.student_id
                            WHERE si.class_id = ? AND st.subject_id = ?
                        """
        subjects_id = {}
        for subject in subjects:
            subjects_id[subject] = Subjects().get_id_subject(subject)

        subjects_score = []
        for subject_name in subjects_id:
            self.cursor.execute(query, (class_id, subjects_id[subject_name]))
            students_grades = self.cursor.fetchall()
            score = 0
            len_score = 0
            for student_grade in students_grades:
                len_score += 1
                score += student_grade[0]
            subjects_score.append((subject_name, score / len_score))

        query = """
                                    SELECT st.grade
                                    FROM student_info si
                                    JOIN students st ON si.student_id = st.student_id
                                    WHERE si.class_id = ?
                                """
        self.cursor.execute(query, (class_id,))
        students_grades = self.cursor.fetchall()
        all_score = 0
        len_all_score = 0
        for student_grade in students_grades:
            len_all_score += 1
            all_score += student_grade[0]
        return [all_score / len_all_score, subjects_score]


class SavesDataTeacher(Saves):
    def get_subjects_teacher(self, user_id=None):
        try:
            self.cursor.execute(f"SELECT subject_id FROM teacher_subject where user_id=?", (user_id,))
            result = self.cursor.fetchall()
            lst_subjects = []
            for sub in result:
                self.cursor.execute(f"SELECT name FROM subjects where subject_id=?", (sub[0],))
                lst_subjects.append(self.cursor.fetchone()[0])
            return lst_subjects
        except:
            raise gr.Error("Неверный логин или пароль")

    def get_class_teacher(self, class_id, subject_id):
        query = """
            SELECT si.student_id, si.surname, si.name, si.patronymic, st.grade
            FROM student_info si
            JOIN students st ON si.student_id = st.student_id
            WHERE si.class_id = ? AND st.subject_id = ?
        """
        self.cursor.execute(query, (class_id, subject_id))
        students = self.cursor.fetchall()
        return students

    def get_classes_teacher(self, user_id=None):
        try:
            self.cursor.execute(f"SELECT class_id FROM teacher_class where user_id=?", (user_id,))
            result = self.cursor.fetchall()
            lst_classes = []
            for class_selected in result:
                self.cursor.execute(f"SELECT number, letter FROM classes where class_id=?", (class_selected[0],))
                res = self.cursor.fetchone()
                lst_classes.append(str(res[0]) + str(res[1]))
            return lst_classes
        except:
            raise gr.Error("Неверный логин или пароль")


class SavesDataStudents(Saves):
    def get_data_student(self, user_id=None):
        try:
            self.cursor.execute(f"SELECT student_id FROM user_student WHERE user_id = {user_id}")
            result = self.cursor.fetchone()
            student_id_data = result[0]
            student_id = result

            self.cursor.execute(
                f"select surname, name, patronymic, class_id from student_info where student_id = {student_id_data}")
            student_data = self.cursor.fetchone()
            full_name = student_data[:3]
            class_id = student_data[-1]

            self.cursor.execute(
                f"select number, letter from classes where class_id = {class_id}")
            class_data = self.cursor.fetchone()
            return student_id + full_name + class_data
        except:
            raise gr.Error("Неверный логин или пароль")

    def take_grades(self, student_id):
        self.cursor.execute(f"SELECT subject_id, grade FROM students WHERE student_id = {student_id}")
        result = self.cursor.fetchall()
        grades_subjects = {}

        for subject_grade in result:
            self.cursor.execute(f"SELECT name FROM subjects WHERE subject_id = {subject_grade[0]}")
            name_subject = self.cursor.fetchone()[0]
            grades_subjects[name_subject] = subject_grade[1]

        return grades_subjects

# print(SavesDataTeacher().get_classes_teacher(74))
