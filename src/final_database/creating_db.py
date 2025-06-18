import sqlite3
import pandas as pd
import random
import string
conn = sqlite3.connect('new_database_17.06.db')
df = pd.read_csv('dataset_school_grades.csv')
df.drop('ID', axis=1,inplace=True)
df.drop_duplicates(['Student', 'Class', 'Subject'], inplace=True)
df.loc[df['Class'] == 9, 'Student'] += 73  # Добавил
#df = df[((df['Class'] == 9) & (df['Period'] == 3)) | ((df['Class'] == 11) & df['Period'] == 2) ]
df.to_sql('dataset', con=conn)
student_index = df.Student.unique()
# Генерация данных учеников
random.seed(42)
male_names = ['Алексей', 'Иван', 'Дмитрий', 'Сергей', 'Михаил', 'Павел', 'Егор', 'Николай', 'Виктор', 'Андрей']
female_names = ['Екатерина', 'Анна', 'Мария', 'Ольга', 'Наталья', 'Елена', 'Ирина', 'Татьяна', 'Светлана', 'Любовь']

male_surnames = ['Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Попов', 'Смирнов', 'Васильев', 'Морозов', 'Новиков', 'Фёдоров']
female_surnames = [s + 'а' for s in male_surnames]

male_patronymics = ['Александрович', 'Иванович', 'Дмитриевич', 'Сергеевич', 'Михайлович', 'Павлович', 'Егорович', 'Николаевич', 'Викторович', 'Андреевич']
female_patronymics = ['Александровна', 'Ивановна', 'Дмитриевна', 'Сергеевна', 'Михайловна', 'Павловна', 'Егоровна', 'Николаевна', 'Викторовна', 'Андреевна']

num_total = len(student_index)
num_male = int(num_total*0.5)
num_female = num_total - num_male

male_data = [
    {
        "surname": random.choice(male_surnames),
        "name": random.choice(male_names),
        "patronymic": random.choice(male_patronymics)
    }
    for _ in range(num_male)
]

female_data = [
    {
        "surname": random.choice(female_surnames),
        "name": random.choice(female_names),
        "patronymic": random.choice(female_patronymics)
    }
    for _ in range(num_female)
]

full_data = male_data + female_data
random.shuffle(full_data)

fio = pd.DataFrame(full_data)
student_info = fio.set_index(student_index)

temp_table = pd.DataFrame(student_index, columns=['Student'])
temp_table = temp_table.merge(df[['Student','Class']], on='Student')
temp_table.columns = ['student_id', 'Class']
temp_table.drop_duplicates('student_id', inplace=True)
student_info['student_id'] = student_info.index
student_info = student_info.merge(temp_table, on='student_id')

class_code = [0 for _ in range(student_info.shape[0])]

idx_8 = idx_9 = i = 0
for class_num in student_info['Class'].to_list():
    if class_num == 8:
        class_code[i] = idx_8%3
        idx_8+=1
    elif class_num == 9:
        class_code[i] = 3 + idx_9%2
        idx_9 += 1
    elif class_num == 10:
        class_code[i] = 5
    else:
        class_code[i] = 6
    i += 1

student_info = student_info[['student_id', 'surname', 'name', 'patronymic']]
student_info['class_id'] = class_code
student_info.sort_values('student_id', inplace=True)
student_info.to_sql('student_info', con=conn)  


def generate_accounts(random_seed, n):
    random.seed(random_seed)
    base_words = [
        "sky", "river", "stone", "leaf", "fire", "cloud", "storm", "wolf", "hawk", "tree",
        "wind", "light", "dark", "moon", "star", "snow", "rock", "grass", "wave", "sun"
    ]
    logins = set()
    while len(logins) < n:
        word = random.choice(base_words)
        number = random.randint(10, 99)
        login = f"{word}_{number}"
        logins.add(login)
    logins = list(logins)
    characters = string.ascii_letters + string.digits
    passwords = [''.join(random.choices(characters, k=8)) for _ in range(n)]
    phones = [f"8{random.randint(9000000000, 9999999999)}" for _ in range(n)]
    domains = ["example.com", "mail.com", "test.org", "demo.net"]
    emails = [f"{login}@{random.choice(domains)}" for login in logins]
    accounts_df = pd.DataFrame({
        "login": logins,
        "password": passwords,
        "phone": phones,
        "email": emails
    })
    return accounts_df


site_user = generate_accounts(random_seed=1, n=student_info.shape[0])
site_user['user_id'] = site_user.index + 1
site_user['type'] = 'student'
site_user = site_user[['user_id', 'login', 'password', 'type', 'phone', 'email']]

user_student = pd.DataFrame(site_user['user_id'].reset_index(drop=True), columns=['user_id'])
user_student['student_id'] = student_info['student_id'].reset_index(drop=True)


teachers = generate_accounts(random_seed=2, n=5)
first_teacher_index = student_info.shape[0] + 1
teachers['user_id'] = teachers.index + first_teacher_index
teachers['type'] = 'teacher'
teachers = teachers[['user_id', 'login', 'password', 'type', 'phone', 'email']]

site_user = pd.concat([site_user, teachers])

parents = generate_accounts(random_seed=3, n=5)
first_parent_index = student_info.shape[0] + 6
parents['user_id'] = parents.index + first_parent_index
parents['type'] = 'parent'
parents = parents[['user_id', 'login', 'password', 'type', 'phone', 'email']]

site_user = pd.concat([site_user, parents])
site_user.loc[len(df)] = [first_parent_index + 5, 'director_52', 'LKjAYs96', 'director', 89054664130, 'director@mail.com']
site_user.to_sql('site_user', conn)