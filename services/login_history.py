from flask_jwt_extended import current_user

from models.login_history import History


def get_history(page: int, number: int) -> list[dict] | dict:
    try:
        user_id = current_user.id
        page = History.get(user_id, page=page, number=number)

        history_list = [
            {
                'email': record.email,
                'login_date': str(record.date)
            } for record in page
        ]

    except Exception:
        raise

    return history_list if history_list else {'msg': 'Never logged in'}
