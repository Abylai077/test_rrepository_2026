-- =====================================================
-- New procedures and function for TSIS 1
-- =====================================================

-- Procedure: add a phone to an existing contact
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone VARCHAR,
    p_type VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id FROM contacts WHERE first_name = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (v_contact_id, p_phone, p_type);
END;
$$;

-- Procedure: move contact to group (creates group if missing)
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id INT;
    v_contact_id INT;
BEGIN
    -- Get or create group
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;
    -- Get contact
    SELECT id INTO v_contact_id FROM contacts WHERE first_name = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;

-- Replace the old search_contacts function (from Practice 8) with extended version
-- that matches name, email, and ANY phone number in the phones table.
DROP FUNCTION IF EXISTS search_contacts(TEXT);

CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(
    id INTEGER,
    first_name VARCHAR,
    phone VARCHAR,      -- keep for backward compatibility (first phone or legacy)
    email VARCHAR,
    birthday DATE,
    group_name VARCHAR,
    all_phones JSONB
) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        c.id,
        c.first_name,
        (SELECT p.phone FROM phones p WHERE p.contact_id = c.id LIMIT 1) AS phone,  -- old field
        c.email,
        c.birthday,
        g.name AS group_name,
        COALESCE(
            (SELECT jsonb_agg(jsonb_build_object('phone', p.phone, 'type', p.type))
             FROM phones p WHERE p.contact_id = c.id),
            '[]'::jsonb
        ) AS all_phones
    FROM contacts c
    LEFT JOIN groups g ON c.group_id = g.id
    WHERE c.first_name ILIKE '%' || p_query || '%'
       OR c.email ILIKE '%' || p_query || '%'
       OR EXISTS (
           SELECT 1 FROM phones p
           WHERE p.contact_id = c.id AND p.phone ILIKE '%' || p_query || '%'
       )
    ORDER BY c.first_name;
END;
$$;