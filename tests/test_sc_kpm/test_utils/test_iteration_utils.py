from sc_client.constants import sc_types
from sc_client.core.sc_client_instance import sc_client
from sc_client.models import ScConstruction, ScLinkContent, ScLinkContentType
from test_sc_kpm.common_tests import BaseTestCase

from sc_kpm.utils import create_links
from sc_kpm.utils.iteration_utils import iter_link_contents_data, iter_links_data


class TestActionUtils(BaseTestCase):
    def test_iter_link_contents_data(self):
        content1 = ScLinkContent(content1_data := "content1", ScLinkContentType.STRING)
        content2 = ScLinkContent(content2_data := "content2", ScLinkContentType.STRING)
        contents = [content1, content2]
        data = [content1_data, content2_data]
        construction = ScConstruction()
        construction.create_link(sc_types.LINK_CONST, content1)
        construction.create_link(sc_types.LINK_CONST, content2)
        links = sc_client.create_elements(construction)
        links_data_from_iterator = list(iter_link_contents_data(contents))
        self.assertEqual(links_data_from_iterator, data)
        sc_client.delete_elements(*links)

    def test_iter_links_data(self):
        links_data = ["content1", "content2"]
        links = create_links(*links_data)
        links_data_from_iterator = list(iter_links_data(links))
        self.assertEqual(links_data_from_iterator, links_data)
        sc_client.delete_elements(*links)
