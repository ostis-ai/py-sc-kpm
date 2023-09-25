from typing import Iterable, Iterator

from sc_client.core.asc_client_instance import asc_client
from sc_client.models import ScAddr
from sc_client.models.sc_construction import ScLinkContentData

from sc_kpm.utils.iteration_utils import iter_link_contents_data


async def iter_links_data(links: Iterable[ScAddr]) -> Iterator[ScLinkContentData]:
    """Iterate by contents data in links"""
    contents = await asc_client.get_link_content(*links)
    return iter_link_contents_data(contents)
