from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from typing import Optional
from datetime import datetime

db = SQLAlchemy()


# Funkcje pomocnicze i wyszukiwania
def convert_to_date(date_string: str) -> str:
    """
    Waliduje wartość tak aby była zgodna z typem date z baz danych Postgres (YYYY-MM-DD).
    """
    try:
        parsed_date = datetime.strptime(date_string, "%Y-%m-%d")
        return parsed_date.date().isoformat()
    except ValueError:
        raise ValueError("Nieprawidłowy format daty. Użyj formatu: YYYY-MM-DD")


def validate_dates(*dates: Optional[str]) -> tuple[Optional[str], ...]:
    """
    Waliduje i konwertuje daty do formatu bazy danych.
    
    Args:
        *dates: Zmienne argumenty dat w formacie YYYY-MM-DD
        
    Returns:
        tuple: Krotka zawierająca skonwertowane daty lub None dla niepodanych dat
        
    Raises:
        ValueError: Jeśli format którejś z dat jest nieprawidłowy
    """
    validated_dates = []
    
    for date in dates:
        if not date:
            validated_dates.append(None)
            continue
            
        try:
            validated_dates.append(convert_to_date(date))
        except ValueError as e:
            raise ValueError(f"Nieprawidłowy format daty: {str(e)}")

    return tuple(validated_dates)


def search_employees(query: str = None, limit: int = None):
    sql = text(f"""
        SELECT *
        FROM users
        WHERE id = (:query)
        {f'LIMIT {limit}' if limit else ''}
    """)
    result = db.session.execute(sql, {'query': f'%{query}%'})


