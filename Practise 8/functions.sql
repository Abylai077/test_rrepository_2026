CREATE OR REPLACE FUNCTION search_contacts(pattern TEXT)
RETURNS TABLE(id INTEGER, first_name VARCHAR, phone VARCHAR) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.phone
    FROM contacts c
    WHERE c.first_name ILIKE '%' || pattern || '%'
       OR c.phone ILIKE '%' || pattern || '%'
    ORDER BY c.first_name;
END; $$;

CREATE OR REPLACE FUNCTION get_contacts_page(p_limit INT, p_offset INT)
RETURNS TABLE(id INTEGER, first_name VARCHAR, phone VARCHAR) LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.phone
    FROM contacts c
    ORDER BY c.first_name
    LIMIT p_limit
    OFFSET p_offset;
END; $$;