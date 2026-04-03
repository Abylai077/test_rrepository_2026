# phonebook.py
import psycopg2
import json
import csv
from connect import get_connection

def create_table():
    """Ensure contacts table exists (matching your Practice 7 schema)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    phone VARCHAR(20) UNIQUE NOT NULL
                );
            """)
        conn.commit()
    print("Table 'contacts' ready.")

def search_contacts(pattern):
    """Call the search_contacts function."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
            rows = cur.fetchall()
    if not rows:
        print("No matches found.")
    else:
        print(f"\nFound {len(rows)} contact(s):")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
    print()

def upsert_contact():
    """Call the upsert procedure."""
    first = input("First name: ").strip()
    phone = input("Phone number: ").strip()
    if not first or not phone:
        print("First name and phone are required.")
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s);", (first, phone))
        conn.commit()
    print("Contact upserted successfully.")

def bulk_insert_from_csv():
    """Read CSV, call bulk_insert_contacts procedure, show invalid records."""
    path = input("CSV file path (default: contacts.csv): ").strip()
    if not path:
        path = "contacts.csv"
    contacts = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contacts.append({
                    "first_name": row.get("first_name", ""),
                    "phone": row.get("phone", "")
                })
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    if not contacts:
        print("No data found.")
        return

    contacts_json = json.dumps(contacts)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.callproc('bulk_insert_contacts', (contacts_json,))
            invalid = cur.fetchone()[0]
            if invalid:
                print("\n❌ Invalid records (skipped):")
                for inv in json.loads(invalid):
                    print(f"  {inv}")
            else:
                print("✅ All records inserted/updated successfully.")
        conn.commit()

def paginated_view():
    """Call get_contacts_page function with user input."""
    try:
        limit = int(input("Contacts per page: "))
        page = int(input("Page number (starting from 1): "))
        if limit <= 0 or page <= 0:
            raise ValueError
    except ValueError:
        print("Please enter positive integers.")
        return
    offset = (page - 1) * limit
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_page(%s, %s);", (limit, offset))
            rows = cur.fetchall()
    if not rows:
        print("No contacts on this page.")
    else:
        print(f"\n--- Page {page} (showing {len(rows)} contacts) ---")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
    print()

def delete_by_identifier():
    """Call delete procedure after confirmation."""
    identifier = input("Enter first name or phone number to delete: ").strip()
    if not identifier:
        print("No identifier given.")
        return
    # Preview matches
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (identifier,))
            matches = cur.fetchall()
    if not matches:
        print("No matching contacts found.")
        return
    print("\nMatching contacts:")
    for row in matches:
        print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
    confirm = input("\nDelete ALL these contacts? (y/n): ").strip().lower()
    if confirm == 'y':
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL delete_contact_by_identifier(%s);", (identifier,))
            conn.commit()
        print("Deletion complete.")
    else:
        print("Cancelled.")

def show_all_contacts():
    """Quick view using search function with empty pattern."""
    search_contacts("")

def menu():
    print("1. Insert/Update contact (upsert)")
    print("2. Bulk insert from CSV (with validation)")
    print("3. Search contacts by pattern")
    print("4. Paginated view")
    print("5. Delete contact(s) by identifier")
    print("6. Show all contacts")
    print("0. Exit")
    return input("Your choice: ").strip()

def main():
    create_table()
    while True:
        choice = menu()
        if choice == '1':
            upsert_contact()
        elif choice == '2':
            bulk_insert_from_csv()
        elif choice == '3':
            pattern = input("Enter search pattern: ").strip()
            search_contacts(pattern)
        elif choice == '4':
            paginated_view()
        elif choice == '5':
            delete_by_identifier()
        elif choice == '6':
            show_all_contacts()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()