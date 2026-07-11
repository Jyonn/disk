import json
import logging
import time
from typing import Any

import requests
from oba import Obj
from smartdjango import Code, Error, OK


logger = logging.getLogger(__name__)


def _redact(value, keep_start=6, keep_end=4):
    if value is None:
        return None
    text = str(value)
    if len(text) <= keep_start + keep_end:
        return text
    return '%s...%s' % (text[:keep_start], text[-keep_end:])


@Error.register
class QitianErrors:
    QITIAN_GET_USER_INFO_FAIL = Error("齐天簿获取用户信息失败", code=Code.InternalServerError)
    QITIAN_GET_USER_PHONE_FAIL = Error("齐天簿获取用户手机号失败", code=Code.InternalServerError)
    QITIAN_AUTH_FAIL = Error("齐天簿身份认证失败", code=Code.InternalServerError)
    QITIAN_REQ_FAIL = Error("齐天簿请求{target}失败", code=Code.InternalServerError)


class ResilientQitianManager:
    def __init__(self, app_id, app_secret, host, timeout=5, retries=3, retry_delay=0.35):
        self.app_id = app_id
        self.app_secret = app_secret
        self.host = (host or '').rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.retry_delay = retry_delay
        self.session = requests.Session()

    def get_token(self, code):
        return self._request(
            method='POST',
            path='/oauth/token',
            target='身份认证',
            json=dict(
                code=code,
                app_secret=self.app_secret,
            ),
        )

    def get_user_info(self, token):
        return self._request(
            method='GET',
            path='/user/',
            target='用户信息',
            headers=dict(token=token),
        )

    def get_user_phone(self, token):
        return self._request(
            method='GET',
            path='/user/phone/',
            target='用户手机号',
            headers=dict(token=token),
        )

    def _request(self, method, path, target, headers=None, json=None) -> Any:
        if not self.host:
            error = QitianErrors.QITIAN_REQ_FAIL(target=target)
            error.append_msg = '未配置齐天服务地址'
            raise error

        url = self.host + path
        last_error = None
        printable_headers = dict(headers or {})
        if 'token' in printable_headers:
            printable_headers['token'] = _redact(printable_headers['token'])
        printable_json = dict(json or {})
        if 'code' in printable_json:
            printable_json['code'] = _redact(printable_json['code'])
        if 'app_secret' in printable_json:
            printable_json['app_secret'] = _redact(printable_json['app_secret'])

        for attempt in range(1, self.retries + 1):
            started_at = time.time()
            response = None
            print(
                '[disk-backend][qitian] request',
                dict(
                    target=target,
                    attempt='%s/%s' % (attempt, self.retries),
                    method=method,
                    url=url,
                    headers=printable_headers,
                    json=printable_json,
                ),
                flush=True,
            )
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json,
                    timeout=self.timeout,
                )
                response_preview = response.text[:1200]
                print(
                    '[disk-backend][qitian] response',
                    dict(
                        target=target,
                        attempt='%s/%s' % (attempt, self.retries),
                        status_code=response.status_code,
                        text=response_preview,
                    ),
                    flush=True,
                )
                body = self._extract_response(response, target)
                elapsed_ms = int((time.time() - started_at) * 1000)
                print(
                    '[disk-backend][qitian] success',
                    dict(
                        target=target,
                        attempt='%s/%s' % (attempt, self.retries),
                        elapsed_ms=elapsed_ms,
                        body=json_dumps_safe(body),
                    ),
                    flush=True,
                )
                if attempt > 1:
                    logger.info(
                        'Qitian request recovered target=%s attempt=%s status=%s elapsed_ms=%s',
                        target,
                        attempt,
                        response.status_code,
                        elapsed_ms,
                    )
                return body
            except requests.RequestException as err:
                last_error = err
                elapsed_ms = int((time.time() - started_at) * 1000)
                print(
                    '[disk-backend][qitian] request-exception',
                    dict(
                        target=target,
                        attempt='%s/%s' % (attempt, self.retries),
                        elapsed_ms=elapsed_ms,
                        error='%s: %s' % (type(err).__name__, err),
                    ),
                    flush=True,
                )
                logger.warning(
                    'Qitian request exception target=%s attempt=%s/%s elapsed_ms=%s error=%s',
                    target,
                    attempt,
                    self.retries,
                    elapsed_ms,
                    err,
                )
                if attempt >= self.retries:
                    raise self._build_request_error(target, f'{type(err).__name__}: {err}')
            except Error as err:
                last_error = err
                elapsed_ms = int((time.time() - started_at) * 1000)
                print(
                    '[disk-backend][qitian] request-error',
                    dict(
                        target=target,
                        attempt='%s/%s' % (attempt, self.retries),
                        elapsed_ms=elapsed_ms,
                        identifier=err.identifier,
                        append_msg=getattr(err, 'append_msg', ''),
                        details=err.details,
                    ),
                    flush=True,
                )
                logger.warning(
                    'Qitian request failed target=%s attempt=%s/%s elapsed_ms=%s identifier=%s append=%s details=%s',
                    target,
                    attempt,
                    self.retries,
                    elapsed_ms,
                    err.identifier,
                    getattr(err, 'append_msg', ''),
                    err.details,
                )
                if attempt >= self.retries or not self._should_retry_status(response):
                    raise err
            finally:
                if response is not None:
                    response.close()

            time.sleep(self.retry_delay * attempt)

        if isinstance(last_error, Error):
            raise last_error
        raise self._build_request_error(target, str(last_error or 'unknown error'))

    def _extract_response(self, response: requests.Response, target: str):
        if response.status_code != requests.codes.ok:
            raise self._build_request_error(
                target,
                f'HTTP {response.status_code}',
                retryable=self._should_retry_status(response),
            )

        try:
            response_data = Obj(response.json())
        except Exception as err:
            raise self._build_request_error(target, f'响应不是合法 JSON: {err}')

        if response_data.identifier != OK.identifier:
            user_message = getattr(response_data, 'user_message', None) or getattr(response_data, 'msg', None)
            debug_message = getattr(response_data, 'debug_msg', None)
            raise self._build_request_error(
                target,
                user_message or debug_message or response_data.identifier,
                retryable=False,
            )

        return Obj.raw(response_data.body)

    @staticmethod
    def _should_retry_status(response: requests.Response | None) -> bool:
        if response is None:
            return True
        return response.status_code >= 500 or response.status_code == 429

    @staticmethod
    def _build_request_error(target, append_msg, retryable=True):
        error = QitianErrors.QITIAN_REQ_FAIL(
            target=target,
            details=append_msg,
            user_message=f'齐天簿{target}暂时不可用，请稍后重试',
        )
        error.append_msg = append_msg
        error.retryable = retryable
        return error


def json_dumps_safe(value):
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)
