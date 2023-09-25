from sc_client.core.asc_client_instance import asc_client
from test_asc_kpm.base_test_case import AsyncioScKpmTestCase

from asc_kpm.utils import create_links
from asc_kpm.utils.aio_iteration_utils import iter_links_data


class TestActionUtils(AsyncioScKpmTestCase):
    async def test_iter_links_data(self):
        links_data = ["content1", "content2"]
        links = await create_links(*links_data)
        links_data_from_iterator = list(await iter_links_data(links))
        self.assertEqual(links_data_from_iterator, links_data)
        await asc_client.delete_elements(*links)
