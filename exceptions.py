class AssertionError(Exception):
    """выбрасывается когда нет переменных"""
    pass

class SendmessageError(Exception):
    """выбрасывается когда сообщение не отправленно"""
    pass


class PracticumAPIError(Exception):
    """выбрасывается когда нет запросе к API"""
    pass


class FormatError(Exception):
    """выбрасывается если не тот формат"""
    pass


class TokenError(Exception):
    """выбрасывается если нет токена"""
    pass
