import csv
from connect import get_connection

# CREATE (insert from console)
def insert_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contacts (first_name, phone) VALUES (%s, %s)",
        (name, phone)
    )
    conn.commit()
    cur.close()
    conn.close()


# CREATE (insert from CSV) с проверкой дубликатов
def insert_from_csv(filename):
    conn = get_connection()
    cur = conn.cursor()

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute(
                """
                INSERT INTO contacts (first_name, phone)
                VALUES (%s, %s)
                ON CONFLICT (phone) DO NOTHING
                """,
                (row[0], row[1])
            )

    conn.commit()
    cur.close()
    conn.close()
    print("CSV импорт завершён (дубликаты пропущены).")

# READ (query)
def search_contacts(keyword):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM contacts WHERE first_name ILIKE %s OR phone LIKE %s",
        (f"%{keyword}%", f"{keyword}%")
    )

    results = cur.fetchall()
    for row in results:
        print(row)

    cur.close()
    conn.close()


# UPDATE
def update_contact(old_name, new_name=None, new_phone=None):
    conn = get_connection()
    cur = conn.cursor()

    fields = []
    values = []

    if new_name:
        fields.append("first_name=%s")
        values.append(new_name)
    if new_phone:
        fields.append("phone=%s")
        values.append(new_phone)

    if not fields:
        cur.close()
        conn.close()
        return 0  # nothing to update

    query = f"UPDATE contacts SET {', '.join(fields)} WHERE first_name=%s"
    values.append(old_name)

    cur.execute(query, values)
    conn.commit()

    updated_rows = cur.rowcount

    cur.close()
    conn.close()
    return updated_rows

# DELETE
def delete_contact(value):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM contacts WHERE first_name=%s OR phone=%s",
        (value, value)
    )

    conn.commit()
    cur.close()
    conn.close()


# MENU
def menu():
    while True:
        print("\n1. Add Contact")
        print("2. Import CSV")
        print("3. Search")
        print("4. Update")
        print("5. Delete")
        print("6. Exit")

        choice = input("Choose: ")

        if choice == "1":
            name = input("Name: ")
            phone = input("Phone: ")
            insert_contact(name, phone)

        elif choice == "2":
            insert_from_csv("Practise 7/contacts.csv")

        elif choice == "3":
            keyword = input("Search: ")
            search_contacts(keyword)

        elif choice == "4":
            old = input("Old name: ")
            new_name = input("New name (or Enter): ")
            new_phone = input("New phone (or Enter): ")

            update_contact(
                old,
                new_name if new_name else None,
                new_phone if new_phone else None
            )

        elif choice == "5":
            value = input("Enter name or phone to delete: ")
            delete_contact(value)

        elif choice == "6":
            break


if __name__ == "__main__":
    menu()