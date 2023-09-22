from typing import Iterable, Iterator

from sc_client.core.sc_client_instance import sc_client
from sc_client.models import ScAddr
from sc_client.models.sc_construction import ScLinkContent, ScLinkContentData


def iter_link_contents_data(contents: Iterable[ScLinkContent]) -> Iterator[ScLinkContentData]:
    """Iterate by data in link contents"""
    for content in contents:
        yield content.data


def iter_links_data(links: Iterable[ScAddr]) -> Iterator[ScLinkContentData]:
    """Iterate by contents data in links"""
    contents = sc_client.get_link_content(*links)
    return iter_link_contents_data(contents)
