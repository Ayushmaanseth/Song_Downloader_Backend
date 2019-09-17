from falcon import status_codes

ENVIRONMENT = "development"

HTTP_HOST = "0.0.0.0"
HTTP_PORT = 3000
HTTP_ASYNC = False
HTTP_ERROR_MESSAGE = {
    int(error[5:]): getattr(status_codes, error)[4:].lower().replace(" ", "_")
    for error in dir(status_codes)
    if error.startswith("HTTP_") and len(error) == 8
}

CACHE_SIZE = 10_000
