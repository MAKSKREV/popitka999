import streamlit as st
import random
import time
import psycopg2
from psycopg2 import sql

# Подключение к базе данных PostgreSQL
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="Den22113s!",
            host="localhost",
            port="5433"
        )
        return conn
    except Exception as e:
        print('ошибка в подключении к бд')

# Функция для создания таблиц, если они не существуют
def create_tables():
    conn = connect_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    name VARCHAR(50) PRIMARY KEY,
                    password VARCHAR(50) NOT NULL,
                    balance INTEGER NOT NULL DEFAULT 50
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    user_name VARCHAR(50) REFERENCES users(name),
                    item_name VARCHAR(100),
                    item_value INTEGER
                );
            """)

# Функция для регистрации пользователя
def register_user(name, password):
    conn = connect_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM users WHERE name = %s", (name,))
            if cur.fetchone() is not None:
                st.error("Пользователь с таким именем уже существует.")
                st.warning(f"Пользователь: {name} уже зарегистрирован.")
                return None

            initial_balance = 50  # Начальный баланс
            cur.execute("INSERT INTO users (name, password, balance) VALUES (%s, %s, %s)", (name, password, initial_balance))
    return name

# Функция для входа пользователя
def login_user(name, password):
    conn = connect_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE name = %s AND password = %s", (name, password))
            return cur.fetchone() is not None  # Возвращаем True, если пользователь найден

# Функция для получения баланса пользователя
def get_user_balance(name):
    conn = connect_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM users WHERE name = %s", (name,))
            result = cur.fetchone()
            return result[0] if result else None

# Функция для обновления баланса пользователя
def update_user_balance(name, new_balance):
    conn = connect_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET balance = %s WHERE name = %s", (new_balance, name))

# Функция для сохранения выбитого предмета
def save_item(user_name, item_name, item_value):
    conn = connect_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO items (user_name, item_name, item_value) VALUES (%s, %s, %s)", (user_name, item_name, item_value))

# Функция для получения всех выбитых предметов пользователя
def get_user_items(user_name):
    conn = connect_db()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT item_name, item_value FROM items WHERE user_name = %s", (user_name,))
            return cur.fetchall()

# Элементы для игры с шансами
items_with_chances = {
    'image0.webp': (0, 0.5),  # 50% шанс
    'image1.png': (5, 0.2),   # 20% шанс
    'image2.jpg': (15, 0.1),  # 10% шанс
    'image3.webp': (1, 0.008),   # 0,8% шанс
    'image4.webp': (7, 0.005),  # 0,5% шанс
    'image5.webp': (30, 0.001)   # 0,1% шанс
}

def spin_items():
    spin_duration = 3  
    end_time = time.time() + spin_duration
    selected_item = None

    while time.time() < end_time:
        selected_item = random.choices(
            list(items_with_chances.keys()),
            weights=[chance for _, chance in items_with_chances.values()],
            k=1
        )[0]
        time.sleep(0.5)  
    return selected_item

# Создаем таблицы при запуске приложения
create_tables()

# Навигация по страницам
st.sidebar.title("Навигация")
page = st.sidebar.radio("Выберите страницу:", ["Регистрация", "Вход", "Крутилка", "Профиль"])

# Страница регистрации
if page == "Регистрация":
    st.title("Регистрация")
    name = st.text_input("Введите ваше имя:")
    password = st.text_input("Введите пароль:", type='password')

    if st.button("Зарегистрироваться"):
        if name and password:
            with st.spinner("Регистрация..."):
                register_user(name, password)
            st.success(f"Пользователь {name} зарегистрирован с начальным балансом 50!")
        else:
            st.error("Пожалуйста, введите имя и пароль.")

# Страница входа
elif page == "Вход":
    st.title("Вход")
    name = st.text_input("Введите ваше имя:")
    password = st.text_input("Введите пароль:", type='password')

    if st.button("Войти"):
        with st.spinner("Вход в систему..."):
            if login_user(name, password):
                st.session_state.user_name = name  # Сохраняем имя пользователя в session_state
                balance = get_user_balance(name)
                st.session_state.balance = balance  # Сохраняем баланс в session_state
                st.success(f"Добро пожаловать, {name}! Ваш баланс: {balance} звёзд.")
            else:
                st.error("Неверное имя пользователя или пароль.")

# Страница крутилки
elif page == "Крутилка":
    st.title("Крутилка")
    
    if 'user_name' in st.session_state:
        st.write(f"Добро пожаловать, {st.session_state.user_name}! Ваш баланс: {st.session_state.balance} звёзд.")

        # Проверка, достаточно ли средств для крутки
        if st.session_state.balance >= 25:

            if 'spin_button_clicked' not in st.session_state:
                st.session_state.spin_button_clicked = False

            if st.session_state.spin_button_clicked:
                st.button("Крутить!", disabled=True)  # Кнопка отключена после нажатия
                with st.spinner("Раскручиваем барабан..."):
                    selected_item = spin_items()
                    st.image(selected_item, width=200)
                    item_value = items_with_chances[selected_item][0]
                    if item_value == 0 or item_value == 5 or item_value == 15:
                        st.write(f"Вы получили {item_value} звёзд")
                    elif item_value == 1:
                        st.write(f"Вы получили подписку на пробив: {item_value} день")
                    else:
                        st.write(f"Вы получили подписку на пробив: {item_value} дней")

                    # Сохраняем выбитый предмет
                    save_item(st.session_state.user_name, selected_item, item_value)

                    # Обновляем баланс
                    new_balance = st.session_state.balance - 25
                    st.session_state.balance = new_balance
                    update_user_balance(st.session_state.user_name, new_balance)  # Обновляем баланс в базе данных

                st.session_state.spin_button_clicked = False  # Сбрасываем состояние кнопки после выполнения
            else:
                if st.button("Крутить!"):
                    st.session_state.spin_button_clicked = True  # Устанавливаем состояние кнопки при нажатии
        else:
            st.error("Недостаточно средств для крутки. Вам нужно минимум 25 рублей на балансе.")
    else:
        st.error("Пожалуйста, войдите, чтобы играть.")

# Страница профиля
elif page == "Профиль":
    st.title("Профиль")
    
    if 'user_name' in st.session_state:
        st.write(f"Добро пожаловать в ваш профиль, {st.session_state.user_name}!")
        st.write(f"Ваш баланс: {st.session_state.balance} звёзд.")
        
        items_list = get_user_items(st.session_state.user_name)
        
        if items_list:
            st.subheader("Выбитые предметы:")
            for item_name, item_value in items_list:
                if item_value == 0 or item_value == 5 or item_value == 15:
                    st.write(f" {item_value} звёзд")
                    st.image(item_name, width=100)  
                elif item_value == 1:
                    st.write(f"подписка на пробив: {item_value} день")
                    st.image(item_name, width=100) 
                else:
                    st.write(f"подписка на пробив: {item_value} дней")
                    st.image(item_name, width=100)   
        else:
            st.write("Вы пока ничего не выбили.")
    else:
        st.error("Пожалуйста, войдите, чтобы просмотреть свой профиль.")