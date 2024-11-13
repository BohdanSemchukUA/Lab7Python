import psycopg2
from psycopg2 import sql

# Параметри підключення до бази даних
conn = psycopg2.connect(
    dbname="library",
    user="bogdan",
    password="password",
    host="127.0.0.1",
    port="5432"
)

def create_tables():
    with conn:
        with conn.cursor() as cur:
            # Створення таблиці "Фільми"
            cur.execute('''
                CREATE TABLE IF NOT EXISTS Фільми (
                    Код_фільму SERIAL PRIMARY KEY,
                    Назва VARCHAR(255) NOT NULL,
                    Жанр VARCHAR(50) CHECK (Жанр IN ('мелодрама', 'комедія', 'бойовик')),
                    Тривалість INT NOT NULL,
                    Рейтинг DECIMAL(2, 1) DEFAULT 0.0
                );
            ''')

            # Створення таблиці "Кінотеатри"
            cur.execute('''
                CREATE TABLE IF NOT EXISTS Кінотеатри (
                    Код_кінотеатру SERIAL PRIMARY KEY,
                    Назва VARCHAR(255) NOT NULL,
                    Ціна_на_квитки DECIMAL(5, 2) NOT NULL,
                    Кількість_місць INT NOT NULL,
                    Адреса VARCHAR(255),
                    Телефон VARCHAR(15) CHECK (Телефон ~ '^\\d{3}-\\d{3}-\\d{4}$')
                );
            ''')

            # Створення таблиці "Транслювання"
            cur.execute('''
                CREATE TABLE IF NOT EXISTS Транслювання (
                    Код_транслювання SERIAL PRIMARY KEY,
                    Код_фільму INT REFERENCES Фільми(Код_фільму),
                    Код_кінотеатру INT REFERENCES Кінотеатри(Код_кінотеатру),
                    Дата_початку DATE NOT NULL,
                    Термін INT NOT NULL
                );
            ''')

            conn.commit()
            print("Таблиці створені успішно.")

def insert_data():
    with conn:
        with conn.cursor() as cur:
            # Додання даних до таблиці "Фільми"
            movies = [
                ('Фільм1', 'комедія', 120, 7.5),
                ('Фільм2', 'мелодрама', 150, 8.2),
                ('Фільм3', 'бойовик', 130, 6.9)
            ]
            cur.executemany("INSERT INTO Фільми (Назва, Жанр, Тривалість, Рейтинг) VALUES (%s, %s, %s, %s)", movies)

            # Додання даних до таблиці "Кінотеатри"
            cinemas = [
                ('Кінотеатр1', 150.00, 100, 'вул. Лісова, 10', '123-456-7890'),
                ('Кінотеатр2', 200.00, 80, 'вул. Нова, 5', '987-654-3210'),
                ('Кінотеатр3', 120.00, 50, 'вул. Сонячна, 7', '555-123-4567')
            ]
            cur.executemany("INSERT INTO Кінотеатри (Назва, Ціна_на_квитки, Кількість_місць, Адреса, Телефон) VALUES (%s, %s, %s, %s, %s)", cinemas)

            # Додання даних до таблиці "Транслювання"
            screenings = [
                (1, 1, '2024-11-10', 7),
                (2, 2, '2024-11-15', 10),
                (3, 3, '2024-11-18', 5)
            ]
            cur.executemany("INSERT INTO Транслювання (Код_фільму, Код_кінотеатру, Дата_початку, Термін) VALUES (%s, %s, %s, %s)", screenings)

            conn.commit()
            print("Дані додані успішно.")

def execute_queries():
    queries = {
        "Всі комедії за рейтингом": '''
            SELECT Назва, Жанр, Рейтинг FROM Фільми WHERE Жанр = 'комедія' ORDER BY Рейтинг DESC;
        ''',
        "Остання дата показу": '''
            SELECT Назва, Дата_початку, Термін, (Дата_початку + Термін * interval '1 day') AS Кінцева_дата 
            FROM Фільми 
            JOIN Транслювання ON Фільми.Код_фільму = Транслювання.Код_фільму;
        ''',
        "Прибуток від одного показу для кожного кінотеатру": '''
            SELECT Назва, (Ціна_на_квитки * Кількість_місць) AS Максимальний_прибуток
            FROM Кінотеатри;
        '''
    }

    with conn:
        with conn.cursor() as cur:
            for title, query in queries.items():
                cur.execute(query)
                rows = cur.fetchall()
                print(f"\n{title}")
                for row in rows:
                    print(row)

if __name__ == "__main__":
    create_tables()
    insert_data()
    execute_queries()
    conn.close()