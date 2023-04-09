from json import dumps

from pydantic import ValidationError

from api.v1.schemas.endpoints import EndpointModel
from core.logger import log
from models.endpoints import Endpoint

logger = log(__name__)


def add_urls(urls):
    flag = False
    if urls:
        for url in urls:
            try:
                _ = EndpointModel(url=url)
            except ValidationError as e:
                logger.exception(e)
                flag = True
    else:
        flag = True
    if flag:
        raise Exception(dumps({'msg': 'Invalid url(s)'}))
        # abort(Response(response=dumps({'msg': 'Invalid url(s)'}), status=status.HTTP_400_BAD_REQUEST))

    try:
        [Endpoint.add(url) for url in urls]

    except Exception:
        raise

    return 'Success'


def remove_urls(urls):
    try:
        [Endpoint.remove(url) for url in urls]

    except Exception:
        raise

    return 'Success'


def get_urls(page: int, number: int):
    try:
        page = Endpoint.get(page=page, number=number)
        endpoints = [
            {
                'id': str(endpoint.id),
                'url': endpoint.url
            } for endpoint in page
        ]
        endpoints.append({'Total': page.total})

    except Exception:
        raise

    return endpoints
