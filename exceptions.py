class SendmessageError(Exception):
    """выбрасывается когда сообщение не отправленно"""
    pass


class PracticumAPIError(Exception):
    """выбрасывается когда нет запросе к API"""
    pass
