from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()


def get_test():
    query = text(
        """
        SELECT
            *
        FROM
            TEST
        """
    )
    try:
        result = db.session.execute(query).first()
        if result:
            return str(dict(result._mapping))
        else:
            return "Brak wyników w bazie danych."
    except Exception as e:
        print(f"Error fetching data from db: {str(e)}")
        return f"Błąd podczas pobierania danych: {str(e)}"
    

def add_record_to_test(content_value):
    query = text(
        """
        INSERT INTO TEST (content)
        VALUES (:content_value)
        """
    )
    try:
        db.session.execute(query, {"content_value": content_value})
        db.session.commit()
        return "Rekord został dodany do bazy danych ✅"
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting data into db: {str(e)}")
        return f"Błąd podczas dodawania danych: {str(e)}"




def get_computer(pcid: int) -> dict:
    """
    Pobiera informację nt komputera.
    Args:
        pcid (int): ID komputera
    Returns:
        dict: Słownik zawierający informacje o komputerze lub pusty słownik jeśli nie znaleziono
    """
    query = text(
        """
        SELECT 
            k.*,
            p.imie AS wlasciciel_imie,
            p.nazwisko AS wlasciciel_nazwisko
        FROM
            komputery k
        LEFT JOIN
            pracownicy p ON k.wlasciciel = p.pid
        WHERE
            k.pcid = :pcid
        """)
    try:
        result = db.session.execute(query, {'pcid': pcid}).first()
        return dict(result._mapping) if result else {}
    except Exception as e:
        print(f"Error fetching computer details: {str(e)}")
        return {}