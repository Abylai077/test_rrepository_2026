CREATE OR REPLACE PROCEDURE upsert_contact(p_first_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE phone = p_phone) THEN
        UPDATE contacts SET first_name = p_first_name WHERE phone = p_phone;
    ELSE
        INSERT INTO contacts (first_name, phone) VALUES (p_first_name, p_phone);
    END IF;
END; $$;

CREATE OR REPLACE PROCEDURE bulk_insert_contacts(
    IN contacts_data JSONB,
    OUT invalid_records JSONB
) LANGUAGE plpgsql AS $$
DECLARE
    rec RECORD;
    invalid_list JSONB := '[]'::JSONB;
    phone_valid BOOLEAN;
BEGIN
    FOR rec IN SELECT * FROM jsonb_to_recordset(contacts_data) AS x(first_name TEXT, phone TEXT)
    LOOP
        phone_valid := (rec.phone ~ '^[0-9+\-\(\)\s]+$' AND LENGTH(rec.phone) >= 5);
        IF (rec.first_name IS NULL OR rec.first_name = '') OR NOT phone_valid THEN
            invalid_list := invalid_list || jsonb_build_object(
                'first_name', rec.first_name,
                'phone', rec.phone,
                'error', CASE WHEN rec.first_name IS NULL OR rec.first_name = '' THEN 'Missing first name' ELSE 'Invalid phone format' END
            );
        ELSE
            CALL upsert_contact(rec.first_name, rec.phone);
        END IF;
    END LOOP;
    invalid_records := invalid_list;
END; $$;

CREATE OR REPLACE PROCEDURE delete_contact_by_identifier(p_identifier TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    DELETE FROM contacts WHERE first_name = p_identifier OR phone = p_identifier;
END; $$;