from typing import Iterable, Iterator

from sc_client.models import ScAddr
from sc_client.models.sc_construction import ScLinkContent, ScLinkContentData

from aio_sc_kpm.client_ import client


def iter_link_contents_data(contents: Iterable[ScLinkContent]) -> Iterator[ScLinkContentData]:
    """Iterate by data in link contents"""
    for content in contents:
        yield content.data


async def iter_links_data(links: Iterable[ScAddr]) -> Iterator[ScLinkContentData]:
    """Iterate by contents data in links"""
    contents = await client.get_link_content(*links)
    return iter_link_contents_data(contents)
