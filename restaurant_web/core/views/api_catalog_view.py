"""
Каталог эндпоинтов FastAPI: загрузка OpenAPI-схемы через requests.
"""
from collections import OrderedDict

from django.conf import settings
from django.shortcuts import render
import requests

_HTTP_METHODS = frozenset(
    {'get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace'}
)
_METHOD_SORT_ORDER = {
    m: i for i, m in enumerate(
        ('get', 'head', 'options', 'post', 'put', 'patch', 'delete', 'trace')
    )
}


def _parse_openapi_paths(spec: dict) -> list[dict]:
    paths = spec.get('paths') or {}
    rows: list[dict] = []
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            m = method.lower()
            if m not in _HTTP_METHODS or not isinstance(operation, dict):
                continue
            tags = operation.get('tags') or []
            primary_tag = tags[0] if tags else ''
            summary = (
                operation.get('summary')
                or operation.get('operationId')
                or ''
            )
            rows.append({
                'method': m.upper(),
                'path': path,
                'summary': summary,
                'tags': tags,
                'primary_tag': primary_tag,
            })
    rows.sort(
        key=lambda r: (
            r['primary_tag'].lower(),
            r['path'].lower(),
            _METHOD_SORT_ORDER.get(r['method'].lower(), 99),
        )
    )
    return rows


def _group_by_tag(rows: list[dict]) -> OrderedDict[str, list[dict]]:
    groups: OrderedDict[str, list[dict]] = OrderedDict()
    for row in rows:
        tag = row['primary_tag'] or 'Без тега'
        if tag not in groups:
            groups[tag] = []
        groups[tag].append(row)
    return groups


def api_endpoints_catalog_view(request):
    """Страница со списком всех операций из OpenAPI-схемы Restaurant API."""
    openapi_url = settings.API_OPENAPI_URL
    docs_url = f'{settings.API_SERVER_ORIGIN}/docs'
    error_message = None
    endpoints: list[dict] = []

    try:
        response = requests.get(openapi_url, timeout=10)
        response.raise_for_status()
        spec = response.json()
        if not isinstance(spec, dict):
            error_message = 'Ответ OpenAPI не является объектом JSON.'
        else:
            endpoints = _parse_openapi_paths(spec)
    except requests.exceptions.HTTPError as exc:
        error_message = (
            f'Сервер вернул ошибку HTTP при запросе {openapi_url}: {exc}. '
            'Проверьте, что Restaurant API запущен и URL схемы верный.'
        )
    except requests.exceptions.Timeout:
        error_message = (
            f'Превышено время ожидания ответа от {openapi_url}. '
            'Убедитесь, что сервер Restaurant API запущен.'
        )
    except requests.exceptions.RequestException as exc:
        error_message = (
            f'Не удалось загрузить схему OpenAPI ({openapi_url}): {exc}. '
            'Запустите FastAPI (обычно порт 8000) и проверьте API_BASE_URL / API_OPENAPI_URL.'
        )
    except ValueError:
        error_message = f'Ответ по адресу {openapi_url} не является корректным JSON.'

    grouped_endpoints = _group_by_tag(endpoints) if endpoints else OrderedDict()

    return render(
        request,
        'api/endpoints.html',
        {
            'endpoints': endpoints,
            'grouped_endpoints': grouped_endpoints,
            'error_message': error_message,
            'openapi_url': openapi_url,
            'docs_url': docs_url,
            'api_server_origin': settings.API_SERVER_ORIGIN,
        },
    )
