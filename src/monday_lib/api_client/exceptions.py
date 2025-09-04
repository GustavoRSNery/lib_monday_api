class APIError(Exception):
    """Exceção base para erros da nossa biblioteca."""
    pass

class APITimeoutError(APIError):
    """Exceção específica para erros de Timeout (504)."""
    pass