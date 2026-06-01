from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
from googleapiclient.errors import HttpError

RETRY_STATUS_CODES = {429, 500, 502, 503, 504} 

def should_retry(exception:Exception) -> bool:
    if isinstance(exception, HttpError):
        status_code = exception.resp.status
        return status_code in RETRY_STATUS_CODES

    return False

retry_google_api = retry(
    retry=retry_if_exception(should_retry),
    stop=stop_after_attempt(3),
    wait=wait_exponential(
        multiplier=1,
        min=2,
        max=10
    ),
    reraise=True
)