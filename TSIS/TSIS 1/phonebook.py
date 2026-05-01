# phonebook.py
import psycopg2
import json
import csv
from connect import get_connection

# ---------- Existing functions from Practice 7-8 (preserved) ----------
def create_table():
    """Ensure contacts table exists (basic version)."""
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
    """Call the search_contacts function (now extended)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s);", (pattern,))
            rows = cur.fetchall()
    if not rows:
        print("No matches found.")
    else:
        print(f"\nFound {len(rows)} contact(s):")
        for row in rows:
            # row: id, first_name, phone, email, birthday, group_name, all_phones
            print(f"ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}, Email: {row[3]}, Birthday: {row[4]}, Group: {row[5]}")
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
    """Original CSV importer (only phone column, old schema)."""
    path = input("CSV file path (default: contacts.csv): ").strip()
    if not path:
        path = "contacts.csv"
    import os
    if not os.path.exists(path):
        print(f"File not found: {os.path.abspath(path)}")
        return
    contacts = []
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                first = row.get("first_name", "").strip()
                phone = row.get("phone", "").strip()
                if first and phone:
                    contacts.append({"first_name": first, "phone": phone})
        print(f"Loaded {len(contacts)} records")
    except Exception as e:
        print(f"CSV read error: {e}")
        return
    if not contacts:
        print("No valid data.")
        return
    contacts_json = json.dumps(contacts, ensure_ascii=False)
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL bulk_insert_contacts(%s::jsonb, NULL::jsonb);", (contacts_json,))
                conn.commit()
                result = cur.fetchone()
                if result and result[0]:
                    print("\n❌ Invalid records (skipped):", result[0])
                else:
                    print("✅ All records inserted/updated successfully.")
    except Exception as e:
        print(f"Database error: {e}")

def paginated_view():
    """Original paginated view (single page)."""
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
    """Delete by identifier (name or phone, case‑insensitive partial match)."""
    identifier = input("Enter first name or phone number to delete: ").strip()
    if not identifier:
        print("No identifier given.")
        return
    # Preview matches using extended search
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, first_name, phone FROM search_contacts(%s);", (identifier,))
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
                # We'll delete using ILIKE pattern (matching preview logic)
                cur.execute("DELETE FROM contacts WHERE first_name ILIKE %s OR phone ILIKE %s;",
                            (f'%{identifier}%', f'%{identifier}%'))
            conn.commit()
        print("Deletion complete.")
    else:
        print("Cancelled.")

def show_all_contacts():
    """Quick view using search function with empty pattern."""
    search_contacts("")

# ---------- New functions for TSIS 1 ----------

def add_phone_to_contact():
    """Calls add_phone procedure."""
    name = input("Contact first name: ").strip()
    if not name:
        print("Name required.")
        return
    phone = input("Phone number: ").strip()
    if not phone:
        print("Phone required.")
        return
    ptype = input("Type (home/work/mobile): ").strip().lower()
    if ptype not in ('home', 'work', 'mobile'):
        print("Invalid type. Using 'mobile'.")
        ptype = 'mobile'
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL add_phone(%s, %s, %s);", (name, phone, ptype))
            conn.commit()
        print("Phone added successfully.")
    except Exception as e:
        print(f"Error: {e}")

def move_contact_to_group():
    """Calls move_to_group procedure."""
    name = input("Contact first name: ").strip()
    if not name:
        print("Name required.")
        return
    group = input("Group name (will be created if missing): ").strip()
    if not group:
        print("Group name required.")
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CALL move_to_group(%s, %s);", (name, group))
            conn.commit()
        print(f"Contact '{name}' moved to group '{group}'.")
    except Exception as e:
        print(f"Error: {e}")

def filter_by_group():
    """Show contacts belonging to a specific group."""
    group = input("Enter group name (Family/Work/Friend/Other or custom): ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.first_name, c.email, c.birthday, g.name AS group_name
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                WHERE g.name = %s
                ORDER BY c.first_name;
            """, (group,))
            rows = cur.fetchall()
    if not rows:
        print(f"No contacts in group '{group}'.")
    else:
        print(f"\nContacts in '{group}':")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Birthday: {row[3]}")
    print()

def search_by_email():
    """Partial match search on email field."""
    pattern = input("Enter email pattern (e.g., 'gmail'): ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, first_name, email, birthday
                FROM contacts
                WHERE email ILIKE %s
                ORDER BY first_name;
            """, (f'%{pattern}%',))
            rows = cur.fetchall()
    if not rows:
        print("No matches.")
    else:
        print(f"\nContacts with email containing '{pattern}':")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Birthday: {row[3]}")
    print()

def sort_contacts():
    """Sort contacts by name, birthday, or date added (id)."""
    print("Sort by:\n1. Name\n2. Birthday\n3. Date added (id)")
    choice = input("Choice: ").strip()
    if choice == '1':
        order_by = "first_name"
    elif choice == '2':
        order_by = "birthday NULLS LAST"
    elif choice == '3':
        order_by = "id"
    else:
        print("Invalid choice.")
        return
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT id, first_name, email, birthday
                FROM contacts
                ORDER BY {order_by};
            """)
            rows = cur.fetchall()
    if not rows:
        print("No contacts.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Birthday: {row[3]}")

def paginated_navigation():
    try:
        limit = int(input("Contacts per page: "))
    except ValueError:
        print("Invalid number.")
        return
    page = 1
    while True:
        offset = (page - 1) * limit
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Query that aggregates phones as JSON objects with number and type
                cur.execute("""
                    SELECT c.id, c.first_name,
                           COALESCE(
                               (SELECT jsonb_agg(jsonb_build_object('number', p.phone, 'type', p.type))
                                FROM phones p WHERE p.contact_id = c.id),
                               '[]'::jsonb
                           ) AS phones
                    FROM contacts c
                    ORDER BY c.first_name
                    LIMIT %s OFFSET %s;
                """, (limit, offset))
                rows = cur.fetchall()
        if rows:
            print(f"\n--- Page {page} ---")
            for row in rows:
                contact_id, name, phones_json = row
                if phones_json:
                    phones_str = ", ".join([f"{p['number']} ({p['type']})" for p in phones_json])
                else:
                    phones_str = "no phones"
                print(f"ID: {contact_id}, Name: {name}, Phones: {phones_str}")
            print(f"--- End of page {page} ---")
        else:
            print("No more contacts.")
        cmd = input("[N]ext, [P]rev, [Q]uit: ").strip().lower()
        if cmd == 'n':
            page += 1
        elif cmd == 'p' and page > 1:
            page -= 1
        elif cmd == 'q':
            break
        else:
            print("Invalid command.")

def export_to_json():
    """Export all contacts (with phones and group) to a JSON file."""
    filename = input("Export filename (default: contacts_export.json): ").strip()
    if not filename:
        filename = "contacts_export.json"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.first_name, c.email, c.birthday, g.name AS group_name,
                       (SELECT jsonb_agg(jsonb_build_object('phone', p.phone, 'type', p.type))
                        FROM phones p WHERE p.contact_id = c.id) AS phones
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                ORDER BY c.id;
            """)
            rows = cur.fetchall()
    data = []
    for row in rows:
        contact = {
            "id": row[0],
            "first_name": row[1],
            "email": row[2],
            "birthday": str(row[3]) if row[3] else None,
            "group": row[4],
            "phones": row[5] if row[5] else []
        }
        data.append(contact)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(data)} contacts to {filename}")

def import_from_json():
    """Import contacts from a JSON file with duplicate handling (by name)."""
    filename = input("JSON file to import: ").strip()
    if not filename:
        print("No filename.")
        return
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            contacts_data = json.load(f)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    for contact in contacts_data:
        name = contact.get('first_name')
        if not name:
            print("Skipping contact without name.")
            continue

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM contacts WHERE first_name = %s;", (name,))
                exists = cur.fetchone()

        if exists:
            choice = input(f"Contact '{name}' exists. [S]kip, [O]verwrite, [A]bort? ").strip().lower()
            if choice == 's':
                continue
            elif choice == 'o':
                with get_connection() as conn:
                    with conn.cursor() as cur:
                        # Update basic info
                        cur.execute("""
                            UPDATE contacts
                            SET email = %s, birthday = %s
                            WHERE first_name = %s;
                        """, (contact.get('email'), contact.get('birthday'), name))
                        # Update group
                        group_name = contact.get('group')
                        if group_name:
                            cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
                            gid = cur.fetchone()
                            if not gid:
                                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id;", (group_name,))
                                gid = cur.fetchone()
                            cur.execute("UPDATE contacts SET group_id = %s WHERE first_name = %s;", (gid[0], name))
                        # Delete old phones
                        cur.execute("DELETE FROM phones WHERE contact_id = (SELECT id FROM contacts WHERE first_name = %s);", (name,))
                        # Insert new phones
                        for phone in contact.get('phones', []):
                            cur.execute("""
                                INSERT INTO phones (contact_id, phone, type)
                                SELECT id, %s, %s FROM contacts WHERE first_name = %s;
                            """, (phone.get('phone'), phone.get('type'), name))
                    conn.commit()
                print(f"Overwrote '{name}'.")
            elif choice == 'a':
                break
            else:
                continue
        else:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO contacts (first_name, email, birthday, group_id)
                        VALUES (%s, %s, %s, NULL)
                        RETURNING id;
                    """, (name, contact.get('email'), contact.get('birthday')))
                    contact_id = cur.fetchone()[0]
                    group_name = contact.get('group')
                    if group_name:
                        cur.execute("SELECT id FROM groups WHERE name = %s;", (group_name,))
                        gid = cur.fetchone()
                        if not gid:
                            cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id;", (group_name,))
                            gid = cur.fetchone()
                        cur.execute("UPDATE contacts SET group_id = %s WHERE id = %s;", (gid[0], contact_id))
                    for phone in contact.get('phones', []):
                        cur.execute("""
                            INSERT INTO phones (contact_id, phone, type)
                            VALUES (%s, %s, %s);
                        """, (contact_id, phone.get('phone'), phone.get('type')))
                conn.commit()
            print(f"Inserted '{name}'.")

def extended_csv_import():
    """CSV import that handles new fields: first_name, email, birthday, group, phone_type, phone."""
    path = input("CSV file path (headers: first_name,email,birthday,group,phone_type,phone): ").strip()
    if not path:
        print("No file.")
        return
    import os
    if not os.path.exists(path):
        print("File not found.")
        return
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('first_name', '').strip()
            if not name:
                continue
            email = row.get('email', '').strip() or None
            birthday = row.get('birthday', '').strip() or None
            group = row.get('group', '').strip() or None
            phone_type = row.get('phone_type', '').strip().lower()
            phone = row.get('phone', '').strip()
            if not phone:
                continue
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM contacts WHERE first_name = %s;", (name,))
                    existing = cur.fetchone()
                    if existing:
                        contact_id = existing[0]
                        if group:
                            cur.execute("SELECT id FROM groups WHERE name = %s;", (group,))
                            gid = cur.fetchone()
                            if not gid:
                                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id;", (group,))
                                gid = cur.fetchone()
                            cur.execute("UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s;",
                                        (email, birthday, gid[0], contact_id))
                        else:
                            cur.execute("UPDATE contacts SET email=%s, birthday=%s WHERE id=%s;",
                                        (email, birthday, contact_id))
                    else:
                        cur.execute("""
                            INSERT INTO contacts (first_name, email, birthday, group_id)
                            VALUES (%s, %s, %s, NULL) RETURNING id;
                        """, (name, email, birthday))
                        contact_id = cur.fetchone()[0]
                        if group:
                            cur.execute("SELECT id FROM groups WHERE name = %s;", (group,))
                            gid = cur.fetchone()
                            if not gid:
                                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id;", (group,))
                                gid = cur.fetchone()
                            cur.execute("UPDATE contacts SET group_id=%s WHERE id=%s;", (gid[0], contact_id))
                    # Insert phone (avoid duplicate)
                    cur.execute("SELECT 1 FROM phones WHERE contact_id=%s AND phone=%s;", (contact_id, phone))
                    if not cur.fetchone():
                        cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s);",
                                    (contact_id, phone, phone_type if phone_type in ('home','work','mobile') else 'mobile'))
                conn.commit()
    print("CSV import completed.")

# ---------- Menu and Main ----------
def menu():
    print("\n" + "="*40)
    print("PhoneBook – Main Menu")
    print("="*40)
    print("1. Insert/Update contact (upsert)")
    print("2. Bulk insert from CSV (simple, old format)")
    print("3. Search contacts by pattern (extended)")
    print("4. Paginated view (single page)")
    print("5. Delete contact(s) by identifier")
    print("6. Show all contacts")
    print("7. Filter contacts by group")
    print("8. Search contacts by email")
    print("9. Sort contacts (name/birthday/date added)")
    print("10. Paginated navigation (next/prev)")
    print("11. Add phone number to existing contact")
    print("12. Move contact to group")
    print("13. Export all contacts to JSON")
    print("14. Import contacts from JSON (duplicate handling)")
    print("15. Extended CSV import (with email, group, phones)")
    print("0. Exit")
    return input("Your choice: ").strip()

def main():
    create_table()
    # Optionally, you can run the schema and procedure creation from Python
    # but it's safer to run them manually once.
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
        elif choice == '7':
            filter_by_group()
        elif choice == '8':
            search_by_email()
        elif choice == '9':
            sort_contacts()
        elif choice == '10':
            paginated_navigation()
        elif choice == '11':
            add_phone_to_contact()
        elif choice == '12':
            move_contact_to_group()
        elif choice == '13':
            export_to_json()
        elif choice == '14':
            import_from_json()
        elif choice == '15':
            extended_csv_import()
        elif choice == '0':
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()