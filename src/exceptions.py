import logging
logging.basicConfig(
    filename="../rigstat.log",
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class RigStatError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        logging.error(f"{self.__class__.__name__}: {message}")


class ApiError(RigStatError):
    pass


class ApiConnectionError(ApiError):
    pass


class ApiAuthError(ApiError):
    pass
