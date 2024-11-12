from common_tests import BaseTestCase
from sc_client.client import generate_elements, erase_elements
from sc_client.constants import sc_type
from sc_client.models import ScConstruction, ScLinkContent, ScLinkContentType

from sc_kpm.utils import generate_links
from sc_kpm.utils.iteration_utils import iter_link_contents_data, iter_links_data


class TestActionUtils(BaseTestCase):
    def test_iter_link_contents_data(self):
        content1 = ScLinkContent(content1_data := "content1", ScLinkContentType.STRING)
        content2 = ScLinkContent(content2_data := "content2", ScLinkContentType.STRING)
        contents = [content1, content2]
        data = [content1_data, content2_data]
        construction = ScConstruction()
        construction.generate_link(sc_type.CONST_NODE_LINK, content1)
        construction.generate_link(sc_type.CONST_NODE_LINK, content2)
        links = generate_elements(construction)
        links_data_from_iterator = list(iter_link_contents_data(contents))
        self.assertEqual(links_data_from_iterator, data)
        erase_elements(*links)

    def test_iter_links_data(self):
        links_data = ["content1", "content2"]
        links = generate_links(*links_data)
        links_data_from_iterator = list(iter_links_data(links))
        self.assertEqual(links_data_from_iterator, links_data)
        erase_elements(*links)
